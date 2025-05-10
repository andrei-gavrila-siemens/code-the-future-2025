from flask import Flask, Response, jsonify
from picamera2 import Picamera2
import cv2
import time

app = Flask(__name__)
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (320, 240)}))
picam2.start()
picam2.set_controls({"AwbMode": 0, "FrameDurationLimits": (66667, 66667)})  # Set white balance to auto

# Global variables
flip_state = {"vertical": True}
current_color = "red"  # Default color

# Color ranges in HSV
color_ranges = {
    "red": {
        "lower1": (0, 50, 50),
        "upper1": (10, 255, 255),
        "lower2": (170, 50, 50),
        "upper2": (180, 255, 255)
    },
    "blue": {
        "lower1": (100, 50, 50),
        "upper1": (130, 255, 255),
        "lower2": None,
        "upper2": None
    },
    "green": {
        "lower1": (40, 50, 50),
        "upper1": (80, 255, 255),
        "lower2": None,
        "upper2": None
    },
    "white": {
        "lower1": (0, 0, 200),
        "upper1": (180, 30, 255),
        "lower2": None,
        "upper2": None
    }
}

def generate_frames():
    while True:
        frame = picam2.capture_array()
        frame = cv2.flip(frame, 1)
        if flip_state["vertical"]:
            frame = cv2.flip(frame, 0)
        
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        
        # Get current color range
        color_range = color_ranges[current_color]
        
        # Create mask for the current color
        mask1 = cv2.inRange(hsv, color_range["lower1"], color_range["upper1"])
        if color_range["lower2"] is not None:
            mask2 = cv2.inRange(hsv, color_range["lower2"], color_range["upper2"])
            mask = mask1 | mask2
        else:
            mask = mask1
            
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw contours on the original frame
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
        
        # Enlarge the frame to 640x480
        enlarged_frame = cv2.resize(frame, (1024, 720), interpolation=cv2.INTER_LINEAR)
        
        # Convert to BGR for encoding
        frame_bgr = cv2.cvtColor(enlarged_frame, cv2.COLOR_RGB2BGR)
        
        # Encode the processed frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame_bgr)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.01)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_flip')
def toggle_flip():
    flip_state["vertical"] = not flip_state["vertical"]
    return jsonify(flip_state)

@app.route('/set_color/<color>')
def set_color(color):
    global current_color
    if color in color_ranges:
        current_color = color
    return jsonify({"current_color": current_color})

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drone Control Console</title>
        <link href="https://fonts.googleapis.com/css?family=Share+Tech+Mono|Orbitron:700&display=swap" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #23272b 0%, #444950 100%);
                font-family: 'Share Tech Mono', 'Orbitron', monospace, Arial, sans-serif;
                color: #e0e0e0;
                margin: 0;
                padding: 0;
                height: 100vh;
            }
            .remote-frame {
                max-width: 900px;
                margin: 40px auto;
                background: #23272b;
                border: 8px solid #888;
                border-radius: 32px;
                box-shadow: 0 0 40px #111, 0 0 0 8px #444 inset;
                display: flex;
                flex-direction: row;
                overflow: hidden;
            }
            .info-panel {
                width: 200px;
                background: linear-gradient(180deg, #2c3136 80%, #23272b 100%);
                border-right: 3px solid #555;
                padding: 24px 12px;
                display: flex;
                flex-direction: column;
                justify-content: flex-start;
                align-items: flex-start;
            }
            .info-panel h2 {
                font-family: 'Orbitron', 'Share Tech Mono', monospace;
                font-size: 1.1em;
                margin: 0 0 18px 0;
                color: #7ecfff;
                letter-spacing: 2px;
            }
            .info-panel .status {
                font-size: 1em;
                margin-bottom: 12px;
                color: #b0ffb0;
            }
            .info-panel .status-label {
                color: #aaa;
                font-size: 0.9em;
            }
            .main-panel {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: space-between;
                padding: 0 0 0 0;
            }
            #videoFeed {
                margin: 32px 0 0 0;
                border: 4px solid #222;
                border-radius: 18px;
                box-shadow: 0 0 24px #000a;
                max-width: 600px;
                width: 90%;
                background: #111;
            }
            .controls {
                margin: 24px 0 0 0;
                display: flex;
                flex-direction: row;
                justify-content: center;
                gap: 18px;
            }
            .metal-btn {
                width: 54px;
                height: 54px;
                border-radius: 50%;
                border: 3px solid #888;
                background: linear-gradient(145deg, #444 60%, #222 100%);
                color: #fff;
                font-family: 'Orbitron', 'Share Tech Mono', monospace;
                font-size: 1.1em;
                font-weight: bold;
                box-shadow: 0 2px 8px #000a, 0 0 0 2px #222 inset;
                margin: 0 6px;
                cursor: pointer;
                transition: background 0.2s, box-shadow 0.2s, border 0.2s;
                outline: none;
            }
            .metal-btn:active {
                background: #222;
                box-shadow: 0 0 0 2px #7ecfff inset;
                border-color: #7ecfff;
            }
            .metal-btn.red { border-color: #ff4444; color: #ff4444; }
            .metal-btn.blue { border-color: #4488ff; color: #4488ff; }
            .metal-btn.green { border-color: #44ff44; color: #44ff44; }
            .metal-btn.white { border-color: #fff; color: #fff; background: #333; }
            .bottom-bar {
                width: 100%;
                background: #23272b;
                border-top: 3px solid #555;
                display: flex;
                flex-direction: row;
                justify-content: space-around;
                align-items: center;
                padding: 10px 0 10px 0;
                box-shadow: 0 -2px 8px #000a;
            }
            .bottom-bar .metal-btn {
                width: 40px;
                height: 40px;
                font-size: 1em;
                margin: 0 2px;
            }
            @media (max-width: 900px) {
                .remote-frame { flex-direction: column; max-width: 98vw; }
                .info-panel { width: 100%; border-right: none; border-bottom: 3px solid #555; flex-direction: row; justify-content: space-between; align-items: center; }
                .main-panel { padding: 0; }
            }
        </style>
    </head>
    <body>
        <div class="remote-frame">
            <div class="info-panel">
                <h2>STATUS</h2>
                <div class="status-label">Mask Color:</div>
                <div class="status" id="colorStatus">Red</div>
                <div class="status-label">Vertical Flip:</div>
                <div class="status" id="flipStatus">ON</div>
            </div>
            <div class="main-panel">
                <img id="videoFeed" src="/video_feed">
                <div class="controls">
                    <button class="metal-btn red" onclick="setColor('red')">R</button>
                    <button class="metal-btn blue" onclick="setColor('blue')">B</button>
                    <button class="metal-btn green" onclick="setColor('green')">G</button>
                    <button class="metal-btn white" onclick="setColor('white')">W</button>
                    <button class="metal-btn" onclick="toggleFlip()">FLIP</button>
                </div>
                <div class="bottom-bar">
                    <p> Drone Live Feed Online </p>
                </div>
            </div>
        </div>
        <script>
            let currentColor = 'red';
            let flipOn = true;
            function toggleFlip() {
                fetch('/toggle_flip')
                    .then(response => response.json())
                    .then(data => {
                        flipOn = data.vertical;
                        document.getElementById('flipStatus').textContent = flipOn ? 'ON' : 'OFF';
                    });
            }
            function setColor(color) {
                fetch(`/set_color/${color}`)
                    .then(response => response.json())
                    .then(data => {
                        currentColor = data.current_color;
                        document.getElementById('colorStatus').textContent = currentColor.charAt(0).toUpperCase() + currentColor.slice(1);
                    });
            }
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)