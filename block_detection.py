import cv2
import numpy as np

def detect_shapes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:  # Skip small noise
            continue
        
        approx = cv2.approxPolqyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
        vertices = len(approx)
        
        # ---- Shape Logic ----
        if vertices == 2:  # Line (Slab)
            cv2.putText(frame, "SLAB", (cnt[0][0][0], cnt[0][0][1]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        elif vertices == 4:  # Rectangle/Block
            (x, y, w, h) = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            if 0.9 <= aspect_ratio <= 1.1:
                cv2.putText(frame, "CUBE", (x, y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            else:
                cv2.putText(frame, "RECTANGLE", (x, y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 100, 0), 2)
        
        elif vertices > 6:  # Circle-like (Cylinder/Arch)
            ellipse = cv2.fitEllipse(cnt)
            (x, y), (ma, MA), angle = ellipse
            
            # Check if it's a semicircle (Arch)
            if angle > 160 and MA / ma > 1.5:  
                cv2.putText(frame, "ARCH", (int(x), int(y)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:  # Assume cylinder
                cv2.putText(frame, "CYLINDER", (int(x), int(y)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    return frame

# Main loop
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    output = detect_shapes(frame)
    cv2.imshow("Block Recognition", output)
    
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()