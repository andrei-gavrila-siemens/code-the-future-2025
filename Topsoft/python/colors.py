import cv2
import numpy as np

def detect_colors_and_boxes_colored(image_path, color_ranges, min_area_threshold, box_thickness=3, text_scale=1, text_thickness=2):
    
    image = cv2.imread(image_path)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    color_bgr_map = {
        'red': (0, 0, 255),
        'blue': (255, 0, 0),
        'green': (0, 255, 0),
        'yellow': (0, 255, 255),
        'orange': (0, 165, 255),  
        'purple': (128, 0, 128)  
    }

    for color_name, ranges in color_ranges.items():
        mask = np.zeros_like(hsv_image[:, :, 0])
        for lower, upper in ranges:
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            color_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
            mask = cv2.bitwise_or(mask, color_mask)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area_threshold:
                x, y, w, h = cv2.boundingRect(contour)
                if color_name in color_bgr_map:
                    color_bgr = color_bgr_map[color_name]
                    cv2.rectangle(image, (x, y), (x + w, y + h), color_bgr, box_thickness)
                    cv2.putText(image, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, text_scale, color_bgr, text_thickness)
                else:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), box_thickness)
                    cv2.putText(image, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0, 255, 0), text_thickness)

    return image

image_path = 'toate.jpeg'  
color_ranges_to_detect = {
    'red': [((0, 70, 50), (10, 255, 255)), ((170, 70, 50), (180, 255, 255))],
    'blue': [((100, 50, 50), (130, 255, 255))],
    'green': [((50, 50, 50), (90, 255, 255))],
    'yellow': [((25, 150, 100), (40, 255, 255))],  
    'orange': [((5, 100, 100), (20, 255, 255))],   
    'purple': [((130, 50, 50), (160, 255, 255))]
}

min_confidence_threshold = 500  
bounding_box_thickness = 5
text_size = 3
text_thickness = 6

processed_image = detect_colors_and_boxes_colored(
    image_path,
    color_ranges_to_detect,
    min_confidence_threshold,
    box_thickness=bounding_box_thickness,
    text_scale=text_size,
    text_thickness=text_thickness
)

cv2.imshow('Color Detection with Colored Boxes', processed_image)
cv2.waitKey(0)
cv2.destroyAllWindows()