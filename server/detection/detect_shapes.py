import cv2
import numpy as np
import datetime
import subprocess
import signal
import time
import os

class ShapeDetector:
    def __init__(self, video_device='/dev/video10', width=640, height=480, framerate=30):
        self.video_device = video_device
        self.width = width
        self.height = height
        self.framerate = framerate
        self.camera_proc = None
        self.cap = None
        self.log_file = open("shapes_log.txt", "a")
        
    def start_camera_stream(self):
        """Start the camera stream and redirect to virtual device"""
        print(f"Starting Pi Camera -> ffmpeg -> {self.video_device} ...")
        
        try:
            self.camera_proc = subprocess.Popen([
                "bash", "-c",
                f"libcamera-vid -t 0 --width {self.width} --height {self.height} "
                f"--framerate {self.framerate} --codec yuv420 --inline -o - "
                f"| ffmpeg -loglevel quiet -f rawvideo -pix_fmt yuv420p "
                f"-s {self.width}x{self.height} -i - -f v4l2 {self.video_device}"
            ], preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN))
            
            # Give the camera time to initialize
            time.sleep(2)
            
            # Open the video capture
            self.cap = cv2.VideoCapture(self.video_device)
            if not self.cap.isOpened():
                print(f"Could not open {self.video_device}.")
                self.cleanup()
                return False
                
            return True
        except Exception as e:
            print(f"Error starting camera: {str(e)}")
            self.cleanup()
            return False
    
    def get_color_name(self, hsv_pixel):
        """Get color name from HSV values"""
        h, s, v = hsv_pixel
        
        # More precise color detection
        if s < 50:
            return "White" if v > 200 else "Gray"
        
        # Handle red which wraps around the hue circle
        if h < 10 or h > 160:
            return "Red"
        elif 10 < h < 25:
            return "Orange"
        elif 25 <= h < 35:
            return "Yellow"
        elif 35 <= h < 85:
            return "Green"
        elif 85 <= h < 130:
            return "Blue"
        elif 130 <= h < 160:
            return "Purple"
        
        return "Unknown"
    
    def classify_shape(self, cnt, approx, area):
        """Classify shape based on contour properties"""
        if area < 300:
            return "Unknown"
            
        sides = len(approx)
        (x, y, w, h) = cv2.boundingRect(approx)
        aspect = w / float(h)
        
        # Calculate circularity (how close to a perfect circle)
        perimeter = cv2.arcLength(cnt, True)
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
        
        # Basic shapes
        if sides == 3:
            return "Triangle"
        elif sides == 4:
            return "Square" if 0.9 <= aspect <= 1.1 else "Rectangle"
        elif circularity > 0.8:
            if h > w * 1.2:
                return "Cylinder"
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
                cv2.imshow("Block Shape + Color Detection", processed_frame)
                
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
        
        # Find white paper
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 60, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Improve white paper detection with morphological operations
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        
        contours_white, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        paper_mask = np.zeros_like(white_mask)
        
        if contours_white:
            largest = max(contours_white, key=cv2.contourArea)
            cv2.drawContours(paper_mask, [largest], -1, 255, -1)
        
        # Detect colored blocks
        lower_color = np.array([0, 50, 50])
        upper_color = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_color, upper_color)
        
        # Improve noise removal with morphological operations
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 300:
                continue
                
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            
            if not self.is_inside_white_bg(cnt, paper_mask):
                continue
                
            # Get shape and color
            shape = self.classify_shape(cnt, approx, area)
            
            x, y, w, h = cv2.boundingRect(cnt)
            color_region = hsv[y + h // 4:y + 3 * h // 4, x + w // 4:x + 3 * w // 4]
            
            if color_region.size > 0:  # Check if region is not empty
                avg_color = cv2.mean(color_region)[:3]
                color_name = self.get_color_name(avg_color)
                
                if shape != "Unknown":
                    label = f"{color_name} {shape}"
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Log detection with timestamp
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.log_file.write(f"{timestamp}: {label}\n")
                    self.log_file.flush()
        
        return frame
    
    def cleanup(self):
        """Clean up resources"""
        print("Shutting down...")
        
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            
        if self.camera_proc is not None:
            self.camera_proc.terminate()
        
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