import json
from picamera2 import Picamera2
import time
import numpy as np
import cv2
import threading

WAIT = 5  
classNames = []
classFile = "/home/SBB/Desktop/Object_Detection_Files/coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/SBB/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/SBB/Desktop/Object_Detection_Files/frozen_inference_graph.pb"
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

object_data_array = [] 
latest_detections = []  
last_detected_object = None
file_lock = threading.Lock()

def getObjects(img, thres=0.45, nms=0.2, draw=True, objects=[]):
    global last_detected_object, latest_detections
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    objectInfo = []
    frame_detections = []  
    img_height, img_width = img.shape[:2]
    if len(objects) == 0:
        objects = classNames
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                x, y, w, h = box
                area = w * h
                dist_to_top = y
                dist_to_left = x
               
                if last_detected_object != className:
                    objectInfo.append([box, className, area, confidence])
                   
                    detection_data = {
                        "object_type": className,
                        "area_pixels": int(area),
                        "width_pixels": int(w),
                        "height_pixels": int(h),
                        "confidence": float(confidence),
                        "dist_to_top_margin_pixels": int(dist_to_top),
                        "dist_to_left_margin_pixels": int(dist_to_left),
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    frame_detections.append(detection_data)
                    with file_lock:
                        object_data_array.append(detection_data) 
                   
                    last_detected_object = className
                if draw:
                    cv2.rectangle(img, box, color=(0, 0, 0), thickness=2)
                    cv2.putText(img, className.upper(), (box[0], box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
                    cv2.putText(img, f"{round(confidence*100, 2)}%", (box[0], box[1] + 60),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
    with file_lock:
        latest_detections = frame_detections 
    return img, objectInfo

def summarize_data():
    summary = {}
    for entry in object_data_array:
        obj_type = entry["object_type"]
        if obj_type not in summary:
            summary[obj_type] = {
                "count": 0,
                "total_area": 0,
                "total_width": 0,
                "total_height": 0,
                "total_dist_to_top": 0,
                "total_dist_to_left": 0
            }
        summary[obj_type]["count"] += 1
        summary[obj_type]["total_area"] += entry["area_pixels"]
        summary[obj_type]["total_width"] += entry["width_pixels"]
        summary[obj_type]["total_height"] += entry["height_pixels"]
        summary[obj_type]["total_dist_to_top"] += entry["dist_to_top_margin_pixels"]
        summary[obj_type]["total_dist_to_left"] += entry["dist_to_left_margin_pixels"]
    return summary

def periodic_file_update():
    while True:
        with file_lock:
            with open("object_detections.json", "w") as f:
                json.dump(latest_detections, f, indent=4)
            with open("summary.json", "w") as f:
                json.dump(summarize_data(), f, indent=4)
        time.sleep(WAIT)

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

file_update_thread = threading.Thread(target=periodic_file_update, daemon=True)
file_update_thread.start()

try:
    while True:
        frame = picam2.capture_array()
       
        frame, objectInfo = getObjects(frame, draw=True)
       
        cv2.imshow("Object Detection", frame)
       
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
