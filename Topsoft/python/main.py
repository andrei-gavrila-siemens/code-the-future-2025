from ultralytics import YOLO
import cv2

# Load the YOLOv11 model. You can specify a pretrained weight file
# (e.g., 'yolo11n.pt' for the nano version) or a custom trained model.
model = YOLO('yolo11n.pt')  # Or 'path/to/your/best.pt'

# Load the image you want to perform object detection on
image_path = '2.jpg'
image = cv2.imread(image_path)

# Perform object detection on the image
results = model(image)

# Process the results
for result in results:
    boxes = result.boxes  # Bounding boxes
    masks = result.masks  # Segmentation masks (if model supports it)
    probs = result.probs  # Class probabilities

    for box in boxes:
        # Get the coordinates of the bounding box
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = box.conf[0]
        class_id = int(box.cls[0])

        # Get the class name from the model's names
        class_name = model.names[class_id]

        # Draw the bounding box and label on the image
        label = f'{class_name}: {confidence:.2f}'
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Display the image with detected objects
cv2.imshow('YOLOv11 Object Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()