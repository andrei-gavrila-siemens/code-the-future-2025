from picamera2 import Picamera2, Preview
from PIL import Image
import numpy as np

# Initializeaza camera cu preview rapid
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
still_config = picam2.create_still_configuration(main={"size": (4056, 3040), "format": "RGB888"})

picam2.configure(preview_config)
picam2.start_preview(Preview.QTGL)
picam2.start()

# Cere numele de baza
base_name = input("Introduceti numele fisierului (ex: cub): ")
count = 1

print("Scrie 'c' + Enter pentru a face o poza, 'q' + Enter pentru a iesi.")

try:
    while True:
        command = input("Comanda: ")
        if command == 'c':
            # Schimba temporar pe configuratia de captura
            picam2.switch_mode(still_config)
            frame = picam2.capture_array()

            # Converteste imaginea in alb-negru
            image = Image.fromarray(frame).convert("L")  # 'L' = grayscale

            filename = f"{base_name}_{count}.png"
            image.save(filename)
            print(f"Poza salvata: {filename}")
            count += 1

            # Revine la configuratia de preview
            picam2.switch_mode(preview_config)

        elif command == 'q':
            print("Iesire program.")
            break

finally:
    picam2.stop_preview()
    picam2.stop()

