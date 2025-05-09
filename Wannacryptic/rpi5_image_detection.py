import csv
from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import numpy as np
import os

app = Flask(__name__)

CSV_FILE = 'shapes_data.csv'

# Asigură-te că fișierul CSV există și are un header
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Formă'])

# Set up camera
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"format": "RGB888"}))
picam2.start()

detected_objects = set()

# Funcție pentru calculul unghiului între 3 puncte
def angle(pt1, pt2, pt3):
    a = np.linalg.norm(pt1 - pt2)
    b = np.linalg.norm(pt2 - pt3)
    c = np.linalg.norm(pt3 - pt1)
    cos_angle = (a * a + b * b - c * c) / (2 * a * b + 1e-6)
    return np.arccos(np.clip(cos_angle, -1.0, 1.0)) * 180 / np.pi

# Funcția de identificare a formelor geometrice
def identify_shapes(frame):
    output = frame.copy()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 200)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            epsilon = 0.04 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            shape = "Necunoscut"

            if len(approx) == 3:
                shape = "Triunghi"
            elif 3 < len(approx) <= 6:
                pts = approx.reshape(-1, 2)
                if len(pts) == 3:
                    shape = "Triunghi"
                elif len(pts) == 4:
                    angles = [angle(pts[i], pts[(i + 1) % 4], pts[(i + 2) % 4]) for i in range(4)]
                    sharp_angles = sum(1 for a in angles if a < 60)
                    if sharp_angles == 1:
                        shape = "Triunghi"
            elif len(approx) == 4:
                (x, y, w, h) = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                if 0.90 <= aspect_ratio <= 1.10:
                    shape = "Patrat"
                else:
                    shape = "Dreptunghi"
            elif len(approx) > 4:
                perimeter = cv2.arcLength(cnt, True)
                if perimeter == 0:
                    continue
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                if circularity > 0.75:
                    shape = "Cerc"

            # Desenăm conturul și eticheta
            x, y, w, h = cv2.boundingRect(cnt)
            cx = x + w // 2
            cy = y + h // 2
            label = f"{shape} ({cx}, {cy})"
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(output, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Salvăm forma în CSV dacă nu a fost deja detectată
            object_id = (cx, cy)
            if object_id not in detected_objects:
                detected_objects.add(object_id)
                with open(CSV_FILE, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([shape])

    return output

# Generator pentru streaming video
def generate():
    while True:
        frame = picam2.capture_array()
        processed_frame = identify_shapes(frame)
        _, buffer = cv2.imencode('.jpg', processed_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video')
def video():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h2>Camera Stream - Detectie Forme Geometrice</h2><img src="/video">'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




shape detection