# pip install easyocr
import easyocr
import cv2



def imgToText(path, langs=['ro','en']):
    reader = easyocr.Reader(langs, gpu=False)
    img  = cv2.imread(path)
    results = reader.readtext(img)
    return [text for _, text, _ in results if text]

def getIndice(lista, valoare):
    for elem in lista:
        if elem.lower() == valoare.lower():
            return lista.index(elem) + 1






