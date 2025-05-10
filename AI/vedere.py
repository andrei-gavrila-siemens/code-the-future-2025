from picamera2 import Picamera2, Preview
import cv2
import numpy as np
import serial
import time

# deschidem serial către Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)

# intervalul de pauză după fiecare trimitere (în secunde)
PAUSE_BETWEEN_SENDS = 5  

def detect_colors(frame, color_ranges, min_area_threshold):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    detected_colors = {}
    for color_name, ranges in color_ranges.items():
        mask = np.zeros_like(frame[:, :, 0])
        for lower, upper in ranges:
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            mask |= cv2.inRange(hsv_frame, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > min_area_threshold:
                x, y, w, h = cv2.boundingRect(contour)
                detected_colors.setdefault(color_name, []).append(((x, y), (x + w, y + h)))
    return detected_colors

if __name__ == "__main__":
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    color_ranges_to_detect = {
        'red':    [((  0,  70,  50), ( 10, 255, 255)), ((170,  70,  50), (180, 255, 255))],
        'blue':   [((100,  50,  50), (130, 255, 255))],
        'green':  [(( 40,  50,  50), ( 90, 255, 255))],
        'yellow': [(( 25, 150, 100), ( 40, 255, 255))],
        'orange': [((  5, 100, 100), ( 20, 255, 255))],
        'purple': [((130,  50,  50), (160, 255, 255))]
    }
    min_area_threshold = 500
    color_draw = {
        'red':    (255,   0,   0),
        'blue':   (  0,   0, 255),
        'green':  (  0, 255,   0),
        'yellow': (255, 255,   0),
        'orange': (255, 165,   0),
        'purple': (128,   0, 128)
    }

    # variabilă pentru a ști când am trimis ultima culoare
    prev_color = None

    try:
        while True:
            frame = picam2.capture_array()
            blurred = cv2.GaussianBlur(frame, (5, 5), 0)
            if blurred is None:
                continue

            frame_with_detections = blurred.copy()
            detected = detect_colors(blurred, color_ranges_to_detect, min_area_threshold)

            # desenăm toate detectările
            for color, boxes in detected.items():
                draw_col = color_draw.get(color, (255,255,255))
                for (x1, y1), (x2, y2) in boxes:
                    cv2.rectangle(frame_with_detections, (x1, y1), (x2, y2), draw_col, 2)
                    text_y = y1-10 if y1>10 else y1+15
                    cv2.putText(frame_with_detections, color, (x1, text_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_col, 2)

            # dacă am detectat cel puțin o culoare și e diferită de precedentă
            if detected:
                current_color = next(iter(detected))   # ia prima culoare detectată
                if current_color != prev_color:
                    msg = f"{current_color}\n".encode()
                    arduino.write(msg)
                    print(f"Sent: {current_color}")
                    prev_color = current_color
                    # pauză ca robotul să apuce cubul
                    time.sleep(PAUSE_BETWEEN_SENDS)
            else:
                # resetăm când nu mai e cubul în cadru
                prev_color = None

            # afișare
            cv2.imshow("Color Detection", cv2.cvtColor(frame_with_detections, cv2.COLOR_RGB2BGR))
            if cv2.waitKey(1) == ord('q'):
                break

    finally:
        picam2.stop()
        picam2.close()
        cv2.destroyAllWindows()
