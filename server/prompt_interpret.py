import cv2
import numpy as np
import datetime
import subprocess
import signal
import time
import os

class ShapeDetector:
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index  # Typically 0 for built-in camera
        self.width = width
        self.height = height
        self.cap = None
        self.log_file = open("shapes_log.txt", "a")
        
    def start_camera_stream(self):
        """Start the laptop camera stream"""
        print("Starting laptop camera...")
        
        try:
            # Open the video capture directly
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            if not self.cap.isOpened():
                print(f"Could not open camera at index {self.camera_index}.")
                self.cleanup()
                return False
                
            return True
        except Exception as e:
            print(f"Error starting camera: {str(e)}")
            self.cleanup()
            return False
    
    def classify_shape(self, cnt, approx, area):
        """Classify shape based on contour properties"""
        if area < 300:
            return "Unknown"
            
        sides = len(approx)
        (x, y, w, h) = cv2.boundingRect(approx)
        
        # Calculate circularity (how close to a perfect circle)
        perimeter = cv2.arcLength(cnt, True)
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
        
        # Basic shapes
        if sides == 3:
            return "Triangle"
        elif sides == 4:
            aspect_ratio = float(w)/h
            if 0.95 <= aspect_ratio <= 1.05:
                return "Square"
            else:
                return "Rectangle"
        elif circularity > 0.8:
            return "Circle"
        elif sides >= 5 and 0.5 <= circularity <= 0.75:
            return "Semicircle"
            
        return "Unknown"
    
    def is_inside_white_bg(self, cnt, paper_mask):
        """Check if contour is inside the white paper background"""
        mask = np.zeros(paper_mask.shape, dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        intersection = cv2.bitwise_and(mask, paper_mask)
        intersect_area = cv2.countNonZero(intersection)
        return intersect_area / cv2.contourArea(cnt) > 0.8 if cv2.contourArea(cnt) > 0 else False
    
    def run_detection(self):
        """Run the shape detection loop"""
        if self.cap is None or not self.cap.isOpened():
            print("Camera not initialized properly")
            return
            
        print("Running detection. Press Q to quit.")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Frame error.")
                    break
                    
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Display results
                cv2.imshow("Shape Detection", processed_frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("Detection stopped by user")
        except Exception as e:
            print(f"Error in detection loop: {str(e)}")
        finally:
            self.cleanup()
    
    def process_frame(self, frame):
        """Process a single frame to detect shapes"""
        # Apply preprocessing
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
        # Find white paper (adjust these values based on your lighting)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 60, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Improve white paper detection
        kernel = np.ones((5, 5), np.uint8)
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
        
        contours_white, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        paper_mask = np.zeros_like(white_mask)
        
        if contours_white:
            largest = max(contours_white, key=cv2.contourArea)
            cv2.drawContours(paper_mask, [largest], -1, 255, -1)
        
        # Detect colored objects (adjust these ranges as needed)
        lower_color = np.array([0, 50, 50])
        upper_color = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_color, upper_color)
        
        # Noise removal
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 300:  # Skip small contours
                continue
                
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            
            if not self.is_inside_white_bg(cnt, paper_mask):
                continue
                
            # Get shape
            shape = self.classify_shape(cnt, approx, area)
            
            # Draw bounding box and label
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, shape, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
        return frame
    
    def cleanup(self):
        """Clean up resources"""
        print("Shutting down...")
        
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            
        if self.log_file is not None:
            self.log_file.close()
            
        cv2.destroyAllWindows()

def main():
    """Main function"""
    detector = ShapeDetector()
    if detector.start_camera_stream():
        detector.run_detection()

if __name__ == "__main__":
    main()