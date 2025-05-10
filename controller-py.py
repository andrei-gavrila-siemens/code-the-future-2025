#!/usr/bin/env python3
import threading
import time
import queue
import json
import serial
import logging
from flask import Flask, render_template, request, jsonify, Response
from detect_shapes import ShapeDetector

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('controller')

# Global variables
shape_queue = queue.Queue()  # Queue for detected shapes
building_queue = queue.Queue()  # Queue for building instructions
current_blueprint = None
arduino_serial = None
system_status = {
    "arduino_connected": False,
    "camera_active": False,
    "building_in_progress": False,
    "current_action": "idle",
    "last_shape_detected": None,
    "error": None
}

# Initialize Flask app
app = Flask(__name__)

# Shape to structure type mapping
SHAPE_STRUCTURE_MAP = {
    "Square": "square",
    "Triangle": "triangle",
    "Circle": "circle",
    "Semicircle": "semicircle"
}

# Structure type to shape mapping (reverse of above)
STRUCTURE_SHAPE_MAP = {v: k for k, v in SHAPE_STRUCTURE_MAP.items()}

def init_arduino(port='/dev/ttyACM0', baudrate=9600, retry_attempts=3):
    """Initialize Arduino connection with retry logic"""
    global arduino_serial, system_status
    
    for attempt in range(retry_attempts):
        try:
            logger.info(f"Attempting to connect to Arduino on {port} (attempt {attempt+1}/{retry_attempts})")
            arduino_serial = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            
            # Wait for ready signal from Arduino
            ready = False
            timeout = time.time() + 5  # 5-second timeout
            while time.time() < timeout:
                if arduino_serial.in_waiting:
                    response = arduino_serial.readline().decode('utf-8').strip()
                    logger.info(f"Arduino response: {response}")
                    if "READY" in response:
                        ready = True
                        break
                time.sleep(0.1)
            
            if ready:
                logger.info("Arduino connection established and ready")
                system_status["arduino_connected"] = True
                return True
            else:
                logger.warning("Arduino did not send ready signal")
                arduino_serial.close()
        except Exception as e:
            logger.error(f"Error connecting to Arduino: {e}")
            if arduino_serial:
                try:
                    arduino_serial.close()
                except:
                    pass
        
        logger.info(f"Retrying in 2 seconds...")
        time.sleep(2)
    
    system_status["error"] = "Failed to connect to Arduino"
    logger.error("All connection attempts to Arduino failed")
    return False

def send_to_arduino(command):
    """Send command to Arduino with response checking"""
    global system_status
    
    if arduino_serial and arduino_serial.is_open:
        try:
            # Clear any pending data
            arduino_serial.reset_input_buffer()
            
            # Send command
            cmd_bytes = (command + "\n").encode()
            arduino_serial.write(cmd_bytes)
            logger.info(f"Sent to Arduino: {command}")
            
            # Wait for response
            timeout = time.time() + 10  # 10-second timeout for command execution
            while time.time() < timeout:
                if arduino_serial.in_waiting:
                    response = arduino_serial.readline().decode('utf-8').strip()
                    logger.info(f"Arduino response: {response}")
                    
                    if "COMPLETE" in response:
                        return True
                    elif "ERROR" in response:
                        system_status["error"] = f"Arduino error: {response}"
                        return False
                time.sleep(0.1)
            
            system_status["error"] = "Arduino command timed out"
            logger.warning(f"Command timed out: {command}")
            return False
        except Exception as e:
            system_status["error"] = f"Error communicating with Arduino: {str(e)}"
            logger.error(f"Error sending command to Arduino: {e}")
            return False
    else:
        system_status["error"] = "Arduino not connected"
        logger.warning("Arduino connection not available")
        return False

def shape_detection_thread():
    """Thread function for shape detection"""
    global system_status
    
    logger.info("Starting shape detection thread")
    system_status["current_action"] = "initializing camera"
    
    detector = ShapeDetector()
    
    # Override the send_arduino_trigger method to use our queue instead
    def custom_send_arduino_trigger(detector_self, center_x, center_y):
        shape = detector_self.lastShape
        if shape in detector_self.valid_shapes:
            # Convert to physical coordinates (calibration needed)
            # Put the detected shape info in the queue
            shape_data = {
                "shape": shape,
                "x": float(center_x),
                "y": float(center_y),
                "timestamp": time.time()
            }
            shape_queue.put(shape_data)
            system_status["last_shape_detected"] = shape_data
            logger.info(f"Detected {shape} at ({center_x}, {center_y})")
    
    # Replace the method
    detector.send_arduino_trigger = lambda x, y: custom_send_arduino_trigger(detector, x, y)
    
    # Start the camera and run detection
    if detector.start_camera_stream():
        system_status["camera_active"] = True
        system_status["current_action"] = "detecting shapes"
        try:
            logger.info("Running shape detection")
            detector.run_detection()
        except Exception as e:
            system_status["error"] = f"Camera error: {str(e)}"
            logger.error(f"Error in shape detection: {e}")
            system_status["camera_active"] = False
        finally:
            detector.cleanup()
            system_status["camera_active"] = False
    else:
        system_status["error"] = "Failed to initialize camera"
        logger.error("Failed to start camera stream")

def building_thread():
    """Thread function for building process"""
    global current_blueprint, system_status
    
    logger.info("Starting building thread")
    
    building_state = {
        "in_progress": False,
        "current_block_index": 0,
        "waiting_for_shape": False,
        "needed_shape": None,
        "total_blocks": 0,
        "completed_blocks": 0
    }
    
    while True:
        try:
            # Check if we have a blueprint to build
            if current_blueprint and not building_state["in_progress"]:
                logger.info("Starting new building process")
                system_status["building_in_progress"] = True
                system_status["current_action"] = "starting new build"
                
                building_state["in_progress"] = True
                building_state["current_block_index"] = 0
                building_state["waiting_for_shape"] = False
                building_state["total_blocks"] = len(current_blueprint["blocks"])
                building_state["completed_blocks"] = 0
            
            # If we're building and not waiting for a shape, request the next block
            if building_state["in_progress"] and not building_state["waiting_for_shape"]:
                # Get the next block from the blueprint
                if building_state["current_block_index"] < len(current_blueprint["blocks"]):
                    block = current_blueprint["blocks"][building_state["current_block_index"]]
                    
                    # What shape do we need?
                    shape_type = block["type"]
                    
                    # Update status
                    building_state["waiting_for_shape"] = True
                    building_state["needed_shape"] = shape_type
                    system_status["current_action"] = f"waiting for {shape_type} shape"
                    
                    logger.info(f"Waiting for {shape_type} shape")
                else:
                    # We've completed the blueprint
                    logger.info("Building complete!")
                    current_blueprint = None
                    building_state["in_progress"] = False
                    system_status["building_in_progress"] = False
                    system_status["current_action"] = "build complete"
            
            # Check if we have detected shapes to use
            if not shape_queue.empty() and building_state["waiting_for_shape"]:
                shape_data = shape_queue.get()
                
                # Check if this shape matches what we need
                detected_shape = SHAPE_STRUCTURE_MAP.get(shape_data["shape"])
                
                if detected_shape == building_state["needed_shape"]:
                    # We have the right shape! Send commands to the Arduino
                    block = current_blueprint["blocks"][building_state["current_block_index"]]
                    
                    # Update status
                    system_status["current_action"] = f"picking up {detected_shape}"
                    
                    # Command to pick up the shape
                    pickup_cmd = f"PICKUP:{shape_data['x']:.1f}:{shape_data['y']:.1f}"
                    if send_to_arduino(pickup_cmd):
                        # Update status
                        system_status["current_action"] = f"placing {detected_shape} at position ({block['x']}, {block['y']})"
                        
                        # Command to place the shape
                        place_cmd = f"PLACE:{block['x']}:{block['y']}"
                        if send_to_arduino(place_cmd):
                            # Move to the next block
                            building_state["current_block_index"] += 1
                            building_state["waiting_for_shape"] = False
                            building_state["completed_blocks"] += 1
                            
                            logger.info(f"Placed {detected_shape} at grid ({block['x']}, {block['y']})")
                        else:
                            logger.error(f"Failed to place {detected_shape}")
                    else:
                        logger.error(f"Failed to pick up {detected_shape}")
                else:
                    logger.info(f"Detected {detected_shape}, but need {building_state['needed_shape']}")
                    # Put the shape back in the queue for later
                    shape_queue.put(shape_data)
            
            time.sleep(0.1)  # Sleep to prevent high CPU usage
            
        except Exception as e:
            system_status["error"] = f"Building error: {str(e)}"
            logger.error(f"Error in building thread: {e}")
            time.sleep(1)

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    global current_blueprint
    
    message = request.form.get('message')
    if not message:
        return jsonify({'status': 'error', 'message': 'No message provided'}), 400
    
    # Convert the message to lowercase to make the check case-insensitive
    message = message.lower()
    
    # Check for shape keywords and generate blueprint
    blueprint = None
    
    if 'house' in message:
        blueprint = {
            "name": "house",
            "size_x": 1,
            "size_y": 2,
            "blocks": [
                {"type": "square", "x": 0, "y": 0},
                {"type": "triangle", "x": 0, "y": 1}
            ]
        }
    elif 'tower' in message:
        blueprint = {
            "name": "tower",
            "size_x": 1,
            "size_y": 4,
            "blocks": [
                {"type": "square", "x": 0, "y": 0},
                {"type": "square", "x": 0, "y": 1},
                {"type": "square", "x": 0, "y": 2},
                {"type": "circle", "x": 0, "y": 3}  # Added some variety with a circle on top
            ]
        }
    elif 'village' in message:
        blueprint = {
            "name": "village",
            "size_x": 5,
            "size_y": 3,
            "blocks": [
                # First house
                {"type": "square", "x": 0, "y": 0},
                {"type": "triangle", "x": 0, "y": 1},
                
                # Second house
                {"type": "square", "x": 2, "y": 0},
                {"type": "triangle", "x": 2, "y": 1},
                
                # Tower
                {"type": "square", "x": 4, "y": 0},
                {"type": "square", "x": 4, "y": 1},
                {"type": "circle", "x": 4, "y": 2}
            ]
        }
    elif 'castle' in message:
        blueprint = {
            "name": "castle",
            "size_x": 5,
            "size_y": 4,
            "blocks": [
                # Main structure
                {"type": "square", "x": 1, "y": 0},
                {"type": "square", "x": 2, "y": 0},
                {"type": "square", "x": 3, "y": 0},
                
                # Towers
                {"type": "square", "x": 0, "y": 0},
                {"type": "square", "x": 0, "y": 1},
                {"type": "semicircle", "x": 0, "y": 2},
                
                {"type": "square", "x": 4, "y": 0},
                {"type": "square", "x": 4, "y": 1},
                {"type": "semicircle", "x": 4, "y": 2},
                
                # Castle top
                {"type": "triangle", "x": 1, "y": 1},
                {"type": "triangle", "x": 3, "y": 1},
            ]
        }
    
    if blueprint:
        # Set the current blueprint for the building thread
        current_blueprint = blueprint
        return jsonify(blueprint)
    else:
        # Return a consistent error response for unrecognized shapes
        return jsonify({'status': 'error', 'message': 'No recognized shape in the prompt'}), 400

@app.route('/status')
def get_status():
    """API endpoint to get current system status"""
    global system_status, current_blueprint
    
    # Add blueprint info to status if available
    status_copy = system_status.copy()
    if current_blueprint:
        status_copy["blueprint"] = {
            "name": current_blueprint.get("name", "custom"),
            "total_blocks": len(current_blueprint["blocks"]),
            "remaining_blocks": sum(1 for i, block in enumerate(current_blueprint["blocks"]) 
                                  if i >= status_copy.get("completed_blocks", 0))
        }
    
    return jsonify(status_copy)

@app.route('/shapes')
def get_detected_shapes():
    """API endpoint to get currently detected shapes"""
    shapes_list = list(shape_queue.queue)
    return jsonify(shapes_list)

@app.route('/reset', methods=['POST'])
def reset_system():
    """API endpoint to reset the system state"""
    global current_blueprint, system_status
    
    # Clear queues
    while not shape_queue.empty():
        shape_queue.get()
    
    # Reset blueprint
    current_blueprint = None
    
    # Reset status
    system_status["building_in_progress"] = False
    system_status["current_action"] = "idle"
    system_status["error"] = None
    
    # Return home
    if arduino_serial and arduino_serial.is_open:
        send_to_arduino("HOME")
    
    return jsonify({"status": "success", "message": "System reset complete"})

def start_server(host='0.0.0.0', port=5000):
    """Start the Flask server"""
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == "__main__":
    # Initialize Arduino connection
    init_arduino()
    
    # Start shape detection thread
    detection_thread = threading.Thread(target=shape_detection_thread)
    detection_thread.daemon = True
    detection_thread.start()
    
    # Start building thread
    build_thread = threading.Thread(target=building_thread)
    build_thread.daemon = True
    build_thread.start()
    
    # Start Flask server
    logger.info("Starting server on 0.0.0.0:5000")
    start_server()