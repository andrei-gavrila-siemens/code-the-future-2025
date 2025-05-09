import cv2
import numpy as np

def get_pixel_hsv(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        hsv_color = hsv_image[y, x]
        print(f"HSV at ({x}, {y}): {hsv_color}")

image_path = 'toate.jpeg'  
image = cv2.imread(image_path)
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

cv2.imshow('Original Image (Click to get HSV)', image)
cv2.setMouseCallback('Original Image (Click to get HSV)', get_pixel_hsv)

cv2.waitKey(0)
cv2.destroyAllWindows()