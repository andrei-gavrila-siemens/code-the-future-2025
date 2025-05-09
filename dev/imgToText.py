import cv2
import pytesseract
import shutil
import sys
import os



#Functie de setare a Tesseract-ului, elem. cheie pt procesarea textului din img
path = shutil.which("tesseract")
if not path:
    path = r"C:\Users\Alex\Desktop\Heckaton\Tesseract\tesseract.exe"
    if not os.path.exists(path):
        print("Eroare " )
        sys.exit(1)
pytesseract.pytesseract.tesseract_cmd = path

#Functie de extragere a textului din imagine
# path - path imagine
# lang - limba - default: eng
def ImgToText(image_path: str, lang: str = 'eng'):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"img negasita: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.Canny(gray, 90, 150)
    text = pytesseract.image_to_string(gray, lang=lang)
    return text

#din textul extras se pregateste un dictionar in care se aranjeaza fiecare indice.
def prepContent(text):
    split = text.split()
    Content = {}
    for i in range(0, len(split), 2):
        nume = split[i].capitalize()
        valoare = int(split[i+1])
        Content[nume] = valoare
    return Content

def checkContent(Content, val):
    for key, value in Content.items():
        if key.lower() == val.lower():
            return value
    return False

if __name__ == "__main__":
    TextImagine = ImgToText('img_6.png', lang='eng')
    print(TextImagine)
    print(prepContent(TextImagine))
    print(checkContent(prepContent(TextImagine), 'Paracetamol'))






