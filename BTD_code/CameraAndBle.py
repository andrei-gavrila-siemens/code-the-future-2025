from picamera2 import Picamera2
import cv2
import numpy as np
from bluepy import btle
from gpiozero import Button
import time

# BLE Configuration
DEVICE_MAC = "F4:12:FA:9F:30:05" 
SERVICE_UUID = "180C"
CHAR_UUID = "2A56"

# Button Setup
button = Button(17)  
object_sent = "0"   
triangles_sent = "0" 
squares_sent = "0" 
circles_sent = "0" 
rectangles_sent = "0" 

def connect_ble():
    try:
        dev = btle.Peripheral(DEVICE_MAC)
        service = dev.getServiceByUUID(SERVICE_UUID)
        char = service.getCharacteristics(CHAR_UUID)[0]
        return dev, char
    except Exception as e:
        print(f"BLE connection error: {e}")
        return None, None

def identify_shape(contour):
    perimeter = cv2.arcLength(contour, True)
    approximation = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
    num_sides = len(approximation)
    
    if num_sides == 3:
        return "triangle"
    elif num_sides == 4:
        x, y, width, height = cv2.boundingRect(approximation)
        aspect_ratio = width / float(height)
        return "square" if 0.9 <= aspect_ratio <= 1.1 else "rectangle"
    else:
        contour_area = cv2.contourArea(contour)
        (_, _), circle_radius = cv2.minEnclosingCircle(contour)
        return "circle" if abs(1 - (contour_area / (np.pi * circle_radius**2))) < 0.2 else None

def find_colored_objects(image, color_definitions, min_detection_area):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    found_objects = []
    
    for color_name, hsv_ranges in color_definitions.items():
        color_mask = np.zeros_like(hsv_image[:, :, 0])
        for lower_range, upper_range in hsv_ranges:
            mask = cv2.inRange(hsv_image, np.array(lower_range), np.array(upper_range))
            color_mask = cv2.bitwise_or(color_mask, mask)
            
        kernel = np.ones((5, 5), np.uint8)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
            
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_detection_area:
                shape_type = identify_shape(contour)
                if shape_type:
                    x, y, w, h = cv2.boundingRect(contour)
                    found_objects.append({
                        'color': color_name,
                        'shape': shape_type,
                        'position': ((x, y), (x + w, y + h))
                    })
    return found_objects

def main():
    # Initialize BLE
    dev, char = connect_ble()
    
    # Initialize camera
    camera = Picamera2()
    camera_config = camera.create_preview_configuration(main={"size": (640, 480)})
    camera.configure(camera_config)
    camera.start()

    # Color definitions
    COLOR_RANGES = {
        'red': [((0, 100, 100), (10, 255, 255)), ((170, 100, 100), (180, 255, 255))],
        'blue': [((100, 80, 80), (130, 255, 255))],
        'green': [((40, 80, 80), (80, 255, 255))],
        'yellow': [((20, 100, 100), (40, 255, 255))],
        'orange': [((10, 100, 100), (20, 255, 255))],
        'purple': [((130, 80, 80), (160, 255, 255))]
    }

    MIN_AREA = 2000

    try:
        while True:
            frame = camera.capture_array()
            if frame is not None:
                processed_frame = frame.copy()
                detected_items = find_colored_objects(frame, COLOR_RANGES, MIN_AREA)
                
                # Prepare object counts
                object_counts = {
                    'total': len(detected_items),
                    'triangle': 0,
                    'square': 0,
                    'circle': 0,
                    'rectangle': 0
                }
                
                for item in detected_items:
                    if item['shape'] in object_counts:
                        object_counts[item['shape']] += 1
                    
                    # Draw bounding box and label
                    (x1, y1), (x2, y2) = item['position']
                    cv2.rectangle(processed_frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
                    cv2.putText(processed_frame, f"{item['color']} {item['shape']}", 
                               (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                # Display counters
                y_pos = 30
                line_space = 25
                texts = [
                    f"Objects: {object_counts['total']}",
                    f"Triangles: {object_counts['triangle']}",
                    f"Squares: {object_counts['square']}",
                    f"Circles: {object_counts['circle']}",
                    f"Rectangles: {object_counts['rectangle']}"
                ]
                
                for i, text in enumerate(texts):
                    cv2.putText(processed_frame, text, (10, y_pos + i*line_space), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                cv2.imshow("Object Detection", cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR))
                
                # Update message to be sent
                global object_sent
                global triangles_sent
                global squares_sent
                global circles_sent
                global rectangles_sent
                object_sent = str(f"O: {object_counts['total']}")
                triangles_sent = str(f" T: {object_counts['triangle']}")
                squares_sent = str(f" S: {object_counts['square']}")
                circles_sent = str(f" C: {object_counts['circle']}")
                rectangles_sent = str(f" R: {object_counts['rectangle']}")
                sent_msg =triangles_sent + squares_sent + circles_sent + rectangles_sent
                # Check button press
                if button.is_pressed:
                    try:
                        if dev is None or char is None:
                            dev, char = connect_ble()
                        if char:
                            char.write(sent_msg.encode(), withResponse=True)
                            
                            print("Obiecte:"+f"Sent:{object_sent}"+"\nTriangles:"+f"Sent: {triangles_sent}"+"\nSquares:"+f"Sent: {squares_sent}"+"\nCircles:"+f"Sent: {circles_sent}"+"\nRectangles:"+f"Sent: {rectangles_sent}") 
                            time.sleep(1) 
                    except Exception as e:
                        print(f"BLE send error: {e}")
                        dev = None
                        char = None

            if cv2.waitKey(1) == ord('q'):
                break

    finally:
        camera.stop()
        cv2.destroyAllWindows()
        if dev:
            dev.disconnect()

if __name__ == "__main__":
    main()
