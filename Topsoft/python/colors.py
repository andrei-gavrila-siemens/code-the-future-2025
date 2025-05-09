from picamera2 import Picamera2
import cv2
import numpy as np
import time
import serial

def detect_colors(frame, color_ranges, min_area_threshold):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    detected_colors = {}
    for color_name, ranges in color_ranges.items():
        mask = np.zeros_like(hsv_frame[:, :, 0])
        for lower, upper in ranges:
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            color_mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
            mask = cv2.bitwise_or(mask, color_mask)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            detected_colors[color_name] = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area_threshold:
                    x, y, w, h = cv2.boundingRect(contour)
                    detected_colors[color_name].append(((x, y), (x + w, y + h)))
    return detected_colors

def apply_gaussian_blur(frame, kernel_size=(5, 5)):
    """Applies Gaussian blur to the input frame."""
    blurred_frame = cv2.GaussianBlur(frame, kernel_size, 20)
    return blurred_frame

if __name__ == "__main__":
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    color_ranges_to_detect = {
        'red': [((0, 70, 50), (10, 255, 255)), ((170, 70, 50), (180, 255, 255))],
        'blue': [((100, 50, 50), (130, 255, 255))],
        'green': [((50, 50, 50), (90, 255, 255))],
        'yellow': [((25, 150, 100), (40, 255, 255))],
        'orange': [((5, 100, 100), (20, 255, 255))],
        'purple': [((170, 70, 130), (190, 90, 140)),
                   ((140, 40, 150), (165, 180, 255))]
    }
    min_area_threshold = 2000
    color_draw = {
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'green': (0, 255, 0),
        'yellow': (255, 255, 0),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128)
    }

    try:
        ser = serial.Serial('COM3', 9600)  # Open serial port COM3 at 9600 baud rate
        print(f"Serial port COM3 opened successfully.")
    except serial.SerialException as e:
        print(f"Error opening serial port COM3: {e}")
        ser = None

    try:
        while True:
            frame = picam2.capture_array()
            if frame is not None:
                # Apply Gaussian blur here
                blurred_frame = apply_gaussian_blur(frame)

                frame_with_detections = blurred_frame.copy()
                detected_colors = detect_colors(blurred_frame.copy(), color_ranges_to_detect, min_area_threshold)

                if detected_colors:
                    print("Detected colors:")
                    serial_data = ""
                    #1 - rosu
                    #2 - orange
                    #3 - albastru
                    #4 - mov
                    for color, boxes in detected_colors.items():
                        print(f"- {color}: {len(boxes)} objects found")
                        if color == "red":
                            serial_data = '1'
                        elif color == "orange":
                            serial_data = '2'
                        elif color == "purple":
                            serial_data = '3'
                        elif color == "blue":
                            serial_data = '4'

                        draw_color = color_draw.get(color)
                        if draw_color:
                            for (x1, y1), (x2, y2) in boxes:
                                x1_int, y1_int, x2_int, y2_int = int(x1), int(y1), int(x2), int(y2)
                                cv2.rectangle(frame_with_detections, (x1_int, y1_int), (x2_int, y2_int), draw_color, 2)
                                text_x = x1_int
                                text_y = y1_int - 10 if y1_int - 10 > 10 else y1_int + 15
                                cv2.putText(frame_with_detections, color, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_color, 2)

                                # Calculate the center coordinates
                                center_x = (x1_int + x2_int) // 2
                                center_y = (y1_int + y2_int) // 2

                                # Display the center coordinates
                                center_text_x = center_x - 20 if center_x - 20 > 0 else center_x + 5
                                center_text_y = y2_int + 20 if y2_int + 20 < frame_with_detections.shape[0] else y1_int - 20
                                cv2.putText(frame_with_detections, f"({center_x},{center_y})", (center_text_x, center_text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, draw_color, 1)

                        else:
                            print(f"Warning: No draw color defined for '{color}'.")

                    if ser and serial_data:
                        try:
                            ser.write(serial_data.encode('utf-8'))
                            print(f"Sent to serial: {serial_data}")
                        except serial.SerialException as e:
                            print(f"Error writing to serial port: {e}")

                else:
                    print("No colors detected.")
                    if ser:
                        try:
                            ser.write(b"0".encode('utf-8')) # Send a '0' indicating no color detected
                            print(f"Sent to serial: 0")
                        except serial.SerialException as e:
                            print(f"Error writing to serial port: {e}")

                cv2.imshow("Color Detection", cv2.cvtColor(frame_with_detections, cv2.COLOR_RGB2BGR))

            if cv2.waitKey(1) == ord('q'):
                break

    finally:
        picam2.stop()
        picam2.close()
        cv2.destroyAllWindows()
        if ser:
            ser.close()
            print("Serial port closed.")