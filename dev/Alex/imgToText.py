import cv2
import pytesseract
import shutil
import sys
import os



#Functie de setare a Tesseract-ului, elem. cheie pt procesarea textului din img
def setareTesseract(path):
    path = shutil.which("tesseract")
    if not path:
        path = r"/Tesseract/tesseract.exe"
        if not os.path.exists(path):
            sys.exit(1)
    pytesseract.pytesseract.tesseract_cmd = path
    return path

#Functie de extragere
def ImgToText(image_path: str, lang: str = 'eng'):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"img negasita: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.Canny(gray, 90, 150)
    text = pytesseract.image_to_string(gray, lang=lang)
    return text

