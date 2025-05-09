import cv2
import serial
import time
# --- Detectare obiect albastru ---
def detect_blue_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Interval pentru albastru (ajustează dacă e nevoie)
    lower_blue = (100, 150, 50)
    upper_blue = (140, 255, 255)

    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Cel mai mare contur
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500:  # Elimină zgomot
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return (cx, cy), mask, c
    return None, mask, None

# --- Mapare coordonate cameră → braț robotic ---
def map_to_arm_coords(x, y, image_shape):
    img_h, img_w = image_shape[:2]
    arm_x = int((x / img_w) * 180)  # Exemplu: scala între 0-180
    arm_y = int((y / img_h) * 180)
    return arm_x, arm_y

# --- Main loop ---
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    (coords, mask, contour) = detect_blue_object(frame)

    if coords:
        x, y = coords
        # Desenează pe imagine
        cv2.circle(frame, (x, y), 10, (255, 0, 0), -1)
        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)

        # Mapează la coordonate ale brațului
        arm_x, arm_y = map_to_arm_coords(x, y, frame.shape)
        command = f"GRAB {arm_x} {arm_y}\n"
        print(f"[TRIMITE] {command.strip()}")
        arduino.write(command.encode())

        time.sleep(3)  # Așteaptă să apuce obiectul

    # Afișare
    cv2.imshow("Camera", frame)
    cv2.imshow("Masca Albastru", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
