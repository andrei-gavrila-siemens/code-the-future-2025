# camera_search.py

import cv2
import pytesseract
import numpy as np
import logging
import sys
import os

# --- Configurații OCR & ROI ---
# Calea către executabilul tesseract (dacă e nevoie pe Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Dimensiunea și poziția regiunii de interes (ROI) în imagine
ROI_X, ROI_Y, ROI_W, ROI_H = 50,  100,  800,  600

# Câte celule orizontal și vertical să împarți ROI
GRID_COLS, GRID_ROWS = 4, 3

# Lista de medicamente (lowercase, fără diacritice)
VALID_MEDICINES = {'paracetamol', 'aspirina', 'parasinus', 'septogal'}

def search_medicine_with_ocr(image_path: str, med_name: str) -> bool:
    """
    Încarcă imaginea de ansamblu, extrage o ROI,
    o împarte într-un grid de GRID_ROWS x GRID_COLS,
    aplică OCR pe fiecare celulă și caută med_name.
    Returnează True la prima coincidență.
    """
    med = med_name.strip().lower()
    if med not in VALID_MEDICINES:
        logging.warning(f"'{med}' nu e în lista de medicamente valide.")
        return False

    logging.info(f"[OCR] Încep căutarea '{med}' în '{image_path}'")

    img = cv2.imread(image_path)
    if img is None:
        logging.error(f"[OCR] Nu pot încărca imaginea: {image_path}")
        return False

    # 1. Extrage ROI
    roi = img[ROI_Y:ROI_Y+ROI_H, ROI_X:ROI_X+ROI_W]
    h_roi, w_roi = roi.shape[:2]

    # 2. Calculează dimensiunea celulelor
    cell_w = w_roi // GRID_COLS
    cell_h = h_roi // GRID_ROWS

    # 3. Parcurge fiecare celulă
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x1 = col * cell_w
            y1 = row * cell_h
            x2 = x1 + cell_w
            y2 = y1 + cell_h

            cell = roi[y1:y2, x1:x2]
            gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            # opțional: binarizare pentru OCR mai bun
            _, bw = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

            # 4. OCR
            text = pytesseract.image_to_string(
                bw,
                lang='ron+eng',      # română + engleză
                config='--psm 6'     # assumează un bloc uniform de text
            ).strip().lower()

            logging.debug(f"[OCR] Celulă ({row},{col}) text: {text!r}")

            # 5. Dacă textul conține cuvintele din med (ex. paracetamol)
            if med in text:
                # desenează dreptunghi pe ROI complet pentru debug
                top_left = (ROI_X + x1, ROI_Y + y1)
                bottom_right = (ROI_X + x2, ROI_Y + y2)
                cv2.rectangle(img, top_left, bottom_right, (0,0,255), 2)
                cv2.putText(img, med.upper(), (top_left[0], top_left[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
                cv2.imshow("Detected", img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

                logging.info(f"[OCR] Găsit '{med}' în celula ({row},{col})")
                return True

    # 6. Nu s-a găsit
    logging.info(f"[OCR] Nu am găsit '{med}' în ROI.")
    return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s")
    if len(sys.argv) != 3:
        print("Usage: python camera_search.py <med_name> <image_path>")
        sys.exit(1)

    medicine = sys.argv[1].lower()
    image_file = sys.argv[2]
    ok = search_medicine_with_ocr(image_file, medicine)
    if ok:
        print(f"✔ Medicament '{medicine}' găsit în imagine.")
        sys.exit(0)
    else:
        print(f"✘ Medicament '{medicine}' NU a fost găsit.")
        sys.exit(1)
