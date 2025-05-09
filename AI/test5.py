from picamera2 import Picamera2, Preview
import cv2
import numpy as np
import serial
import time

arduino = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)

def detect_colors(frame, color_ranges, min_area_threshold):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    detected_colors = {}
    for color_name, ranges in color_ranges.items():
        mask = np.zeros_like(frame[ :, :, 0])
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

if __name__ == "__main__":
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    # We will display using OpenCV, so no need for the Picamera2 preview window
    # picam2.start_preview(Preview.QTGL)

    picam2.start()

    color_ranges_to_detect = {
        'red': [((0, 70, 50), (10, 255, 255)), ((170, 70, 50), (180, 255, 255))],
        'blue': [((100, 50, 50), (130, 255, 255))],
        'green': [((40, 50, 50), (90, 255, 255))],
        'yellow': [((25, 150, 100), (40, 255, 255))],
        'orange': [((5, 100, 100), (20, 255, 255))],
        'purple': [((130, 50, 50), (160, 255, 255))]
    }
    min_area_threshold = 500
    color_draw = {
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'green': (0, 255, 0),
        'yellow': (255, 255, 0),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128)
    }

    try:
        while True:
            frame = picam2.capture_array()
            blurred = cv2.GaussianBlur(frame, (5, 5), 0)
            if blurred is not None:
                frame_with_detections = blurred
                detected_colors = detect_colors(blurred, color_ranges_to_detect, min_area_threshold)
                last_color = None
                if detected_colors:
                    print("Detected colors:")
                    for color, boxes in detected_colors.items():
                        print(f"- {color}: {len(boxes)} objects found")
                        draw_color = color_draw.get(color)
                        if draw_color:
                            for (x1, y1), (x2, y2) in boxes:
                                x1_int, y1_int, x2_int, y2_int = int(x1), int(y1), int(x2), int(y2)
                                # Draw the bounding box
                                cv2.rectangle(frame_with_detections, (x1_int, y1_int), (x2_int, y2_int), draw_color, 2)
                                # Calculate the position for the text (above the top-left corner)
                                text_x = x1_int
                                text_y = y1_int - 10 if y1_int - 10 > 10 else y1_int + 15 # Adjust if too close to the top
                                # Add the color name text
                                cv2.putText(frame_with_detections, color, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_color, 2)
                        else:
                            print(f"Warning: No draw color defined for '{color}'.")
                    for color in detected_colors:
                        if color == "red":
                            arduino.write(b"red\n")
                            last_color = color
                        elif color == "blue":
                            arduino.write(b"blue\n")
                            last_color = color
                        elif color == "green":
                            arduino.write(b"green\n")
                            last_color = color
                        elif color == "yellow":
                            arduino.write(b"yellow\n")
                            last_color = color    
                        elif color == "orange":
                            arduino.write(b"orange\n")
                            last_color = color
                        elif color == "purple":
                            arduino.write(b"purple\n")
                            last_color = color    


                else:
                    print("No colors detected.")
                    last_color = None


                # Display the frame with bounding boxes and color names
                cv2.imshow("Color Detection", cv2.cvtColor(frame_with_detections, cv2.COLOR_RGB2BGR))

            if cv2.waitKey(1) == ord('q'):
                break
            
            

    finally:
        picam2.stop()
        picam2.close()
        cv2.destroyAllWindows()




