from ultralytics import YOLO
import cv2

model = YOLO('yolo11n.pt')  

image_path = '2.jpg'
image = cv2.imread(image_path)

results = model(image)

for result in results:
    boxes = result.boxes  
    masks = result.masks  
    probs = result.probs  

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = box.conf[0]
        class_id = int(box.cls[0])

        class_name = model.names[class_id]

        label = f'{class_name}: {confidence:.2f}'
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow('YOLOv11 Object Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()