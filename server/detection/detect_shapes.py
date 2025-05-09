import cv2
import numpy as np
import datetime
import subprocess
import signal
import time
import os
from collections import deque

class ShapeDetector:
    def _init_(self, video_device='/dev/video10', width=640, height=480, framerate=60, focus_distance=27):
        self.video_device = video_device
        self.width = width
        self.height = height
        self.framerate = framerate
        self.focus_distance = focus_distance  # Focus distance in cm
        self.camera_proc = None
        self.cap = None
        self.log_file = open("shapes_log.txt", "a")
        self.valid_shapes = ["Square", "Circle", "Semicircle", "Triangle"]
        
         # Constants for detection
        self.min_area = 500  # Minimum area for shape consideration
        self.epsilon_factor = 0.03  # Reduced for more accurate shape detection
        
        # Shadow handling parameters
        self.shadow_threshold = 35  # Threshold for shadow detection
        
        # Setting for camera focus at 27cm height
        self.focus_height = 27  # cm
        
        # Shape tracking for smoother detection
        self.shape_history = {}  # Dictionary to store shape detection history
        self.history_size = 5    # Number of frames to consider for smoothing
        self.min_detection_threshold = 3  # Minimum detections needed to confirm a shape
        
    def start_camera_stream(self):
        """Start the camera stream and redirect to virtual device with error handling"""
        print(f"Starting Pi Camera -> ffmpeg -> {self.video_device} ...")
        
        try:
            # Check if the virtual device exists
            if not os.path.exists(self.video_device):
                print(f"Virtual video device {self.video_device} not found!")
                print("You may need to create it with: sudo modprobe v4l2loopback devices=1")
                return False
                
            self.camera_proc = subprocess.Popen([
                "bash", "-c",
                f"libcamera-vid -t 0 --width {self.width} --height {self.height} "
                f"--framerate {self.framerate} --codec yuv420 --inline "
                f"--lens-position 0.7 "  # Setting focus for ~27cm height
                f"--shutter 10000 "  # Faster shutter speed for higher FPS
                f"-o - | ffmpeg -loglevel quiet -f rawvideo -pix_fmt yuv420p "
                f"-s {self.width}x{self.height} -i - -f v4l2 -pix_fmt yuv420p "
                f"-r {self.framerate} {self.video_device}"
            ], preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN))
            
            # Give the camera time to initialize with status updates
            for i in range(3):
                print(f"Camera initializing ({i+1}/3)...")
                time.sleep(0.5)
            
            # Try multiple times to open the camera
            for attempt in range(3):
                self.cap = cv2.VideoCapture(self.video_device)
                if self.cap.isOpened():
                    # Set camera properties for higher framerate
                    self.cap.set(cv2.CAP_PROP_FPS, self.framerate)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Lower buffer for more recent frames
                    print(f"Camera initialized successfully! Focus set to {self.focus_height}cm height")
                    print(f"Target framerate: {self.framerate} FPS")
                    return True
                else:
                    print(f"Attempt {attempt+1}: Could not open {self.video_device}. Retrying...")
                    time.sleep(1)
            
            print(f"Failed to open {self.video_device} after multiple attempts.")
            self.cleanup()
            return False
                
        except Exception as e:
            print(f"Error starting camera: {str(e)}")
            self.cleanup()
            return False
    
    def set_camera_focus(self):
        """Set camera focus for 27 cm height from table"""
        try:
            # For libcamera-based systems (Raspberry Pi)
            if self.camera_proc is not None:
                print(f"Setting camera focus for {self.focus_height}cm height...")
                
                # Stop existing process
                self.camera_proc.terminate()
                time.sleep(1)
                
                # Start new process with focus settings
                self.camera_proc = subprocess.Popen([
                    "bash", "-c",
                    f"libcamera-vid -t 0 --width {self.width} --height {self.height} "
                    f"--framerate {self.framerate} --codec yuv420 --inline "
                    f"--lens-position 0.7 "  # Setting focus for ~27cm (adjust as needed)
                    f"--shutter 10000 "  # Faster shutter speed for higher FPS
                    f"-o - | ffmpeg -loglevel quiet -f rawvideo -pix_fmt yuv420p "
                    f"-s {self.width}x{self.height} -i - -f v4l2 -pix_fmt yuv420p "
                    f"-r {self.framerate} {self.video_device}"
                ], preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN))
                
                # Give the camera time to adjust
                time.sleep(2)
                
                # Reopen capture
                if self.cap is not None:
                    self.cap.release()
                self.cap = cv2.VideoCapture(self.video_device)
                
                # Set camera properties for higher framerate
                if self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FPS, self.framerate)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                
                return self.cap.isOpened()
            return False
        except Exception as e:
            print(f"Error setting camera focus: {str(e)}")
            return False
    
    def classify_shape(self, cnt, approx, area):
        """Classify shape based on contour properties - only return valid shapes"""
        if area < 300:
            return "Unknown"
            
        sides = len(approx)

        # Calculate circularity (how close to a perfect circle)
        perimeter = cv2.arcLength(cnt, True)
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0

        # Use Hu Moments to help with semicircle detection
        moments = cv2.moments(cnt)
        huMoments = cv2.HuMoments(moments).flatten()
        logHu = -np.sign(huMoments[0]) * np.log10(abs(huMoments[0])) if huMoments[0] != 0 else 0

        # print(sides)
        if sides == 3:
            return "Triangle"
        elif sides == 4:
            return "Square"
        elif circularity > 0.85:
            return "Circle"
        elif 0.2 < circularity < 0.75 and -0.6 < logHu < -0.2:
            return "Semicircle"

        return "Unknown"

    
    def is_inside_white_bg(self, cnt, paper_mask):
        """Check if contour is inside the white paper background"""
        mask = np.zeros(paper_mask.shape, dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        intersection = cv2.bitwise_and(mask, paper_mask)
        intersect_area = cv2.countNonZero(intersection)
        return intersect_area / cv2.contourArea(cnt) > 0.8 if cv2.contourArea(cnt) > 0 else False
    
    def is_colorful(self, color_region):
        """Check if a region is colorful (not gray/shadow)"""
        if color_region.size == 0:
            return False
            
        # Calculate mean saturation value
        mean_sat = np.mean(color_region[:, :, 1])
        # Calculate color variance
        color_variance = np.std(color_region[:, :, 0])
        
        # Region is colorful if it has high saturation and some color variance
        return mean_sat > 80 and color_variance > 5
    
    def run_detection(self):
        """Run the shape detection loop with improved error handling and smoother detection"""
        if self.cap is None or not self.cap.isOpened():
            print("Camera not initialized properly")
            return
            
        print("Running detection. Press Q to quit. Press F to adjust focus.")
        
        try:
            frame_count = 0
            fps_start_time = time.time()
            fps = 0
            
            # For calculating actual processing speed
            process_times = deque(maxlen=30)
            
            while True:
                loop_start = time.time()
                
                ret, frame = self.cap.read()
                if not ret:
                    print("Frame error. Attempting to recover...")
                    # Try to recover connection
                    self.cap.release()
                    time.sleep(0.5)
                    self.cap = cv2.VideoCapture(self.video_device)
                    if self.cap.isOpened():
                        self.cap.set(cv2.CAP_PROP_FPS, self.framerate)
                        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                    else:
                        print("Could not recover camera connection.")
                        break
                    continue
                    
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Display results
                cv2.imshow("Shape Detection", processed_frame)
                
                # Check for keys - using a short wait time for higher responsiveness
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('f'):
                    print("Adjusting camera focus...")
                    self.set_camera_focus()
                    
                # If we're processing frames faster than our target rate, sleep to save CPU
                elapsed = time.time() - loop_start
                target_frame_time = 1.0 / self.framerate
                if elapsed < target_frame_time:
                    time.sleep(target_frame_time - elapsed)
                    
        except KeyboardInterrupt:
            print("Detection stopped by user")
    
    def process_frame(self, frame):
        """Process a single frame to detect colorful shapes"""
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
        
        # Focus on colorful objects (increased saturation threshold)
        # Ignoring grays, shadows by requiring higher saturation values
        lower_color = np.array([0, 100, 50])   # Increased minimum saturation from 50 to 100
        upper_color = np.array([180, 255, 255])
        color_mask = cv2.inRange(hsv, lower_color, upper_color)
        
        # Improve noise removal with morphological operations
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        
        # Find contours
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour
        detected_count = 0
        # print(f'length={len(contours)}')
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 300:
                continue
                
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            
            if not self.is_inside_white_bg(cnt, paper_mask):
                continue
                
            # Get shape
            shape = self.classify_shape(cnt, approx, area)
            
            # Only process valid shapes
            shapeIsInvalid = shape not in self.valid_shapes
            if shapeIsInvalid:
                continue
                
            # Get color information from center region
            x, y, w, h = cv2.boundingRect(cnt)
            color_region = hsv[y + h // 4:y + 3 * h // 4, x + w // 4:x + 3 * w // 4]
            
            # Get the dominant color in BGR
            mean_hsv = cv2.mean(color_region)
            
            # Draw results
            cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
            # cv2.putText(frame, f"{shape}", (x, y - 10), 
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            center_x = (x + w)/2
            center_y = (y + h)/2
            cv2.putText(frame, f"{center_x};{center_y}", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
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
    """Main function with error handling"""
    try:
        print("Starting Shape Detector...")
        detector = ShapeDetector(framerate=60)  # Try to run at 60fps
        if detector.start_camera_stream():
            detector.run_detection()
        else:
            print("Failed to start camera stream. Exiting.")
    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        print("Exiting program")
        if 'detector' in locals():
            detector.cleanup()

if __name__ == "__main__":
    main()