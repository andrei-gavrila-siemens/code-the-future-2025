from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time

app = Flask(__name__)
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (320, 240)}))
picam2.start()
picam2.set_controls({"AwbMode": 0, "FrameDurationLimits": (66667, 66667)})  # Set white balance to auto

def generate_frames():
    while True:
        frame = picam2.capture_array()
        frame = cv2.flip(frame, 1) 
        # Convert directly to HSV (assuming camera outputs RGB)
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        # Define range for red color in HSV
        lower_red1 = (0, 50, 50)
        upper_red1 = (10, 255, 255)
        lower_red2 = (170, 50, 50)
        upper_red2 = (180, 255, 255)
        # Create masks for red
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 | mask2
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Draw contours on the original frame
        cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
        # Enlarge the frame to 640x480
        enlarged_frame = cv2.resize(frame, (1024, 720), interpolation=cv2.INTER_LINEAR)
        # Convert to BGR for encoding (if needed)
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

@app.route('/')
def index():
    return "<h1>Drone Live Feed</h1><img src='/video_feed'>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)