import os
import time
import numpy as np
import tensorflow as tf
from PIL import Image
from picamera2 import Picamera2
import io
import cv2
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from tts import speak  # Importăm funcția TTS

# Încarcă cheia API din fișier .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY lipseste. Verifica fisierul .env.")

genai.configure(api_key=GOOGLE_API_KEY)

# Funcție pentru detectarea culorii folosind Gemini
def get_color_from_gemini(image_pil):
    buffer = io.BytesIO()
    image_pil.save(buffer, format="PNG")
    buffer.seek(0)
    image_bytes = buffer.read()
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = (
            "Spune exact, fara alte detalii, doar numele culorii principale a obiectului din imagine "
            "Nu ghici, raspunde doar daca este sigur. Vezi lucrurile invers portocaliu, galben si maro sunt de fapt albastru. Albastru e de fapt portocaliu. RGB. DETECTEAZA BINE!"
        )
        response = model.generate_content(
            [
                prompt,
                {
                    "mime_type": "image/png",
                    "data": image_bytes
                }
            ],
            generation_config=genai.types.GenerationConfig(max_output_tokens=20)
        )
        return response.text.strip()
    except Exception as e:
        return f"[Eroare Gemini]: {e}"

# Încarcă modelul TensorFlow Lite
interpreter = tf.lite.Interpreter(model_path="model_unquant.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Încarcă etichetele
with open('labels.txt', 'r') as f:
    labels = [line.strip() for line in f.readlines()]

threshold = 0.85
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
picam2.start()

print("Sistem pornit. Caut obiecte...")

last_detected_label = None

try:
    while True:
        frame = picam2.capture_array()

        # Convertim RGB → BGR → RGB pentru test
        bgr_array = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        rgb_array_corrected = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(rgb_array_corrected, 'RGB')

        # Redimensionare doar pentru model
        image_pil_resized = image_pil.resize((224, 224))
        img = np.expand_dims(np.array(image_pil_resized), axis=0).astype(np.float32) / 255.0

        interpreter.set_tensor(input_details[0]['index'], img)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])[0]

        predicted_index = np.argmax(output_data)
        predicted_label = labels[predicted_index]
        confidence = output_data[predicted_index]

        if confidence >= threshold:
            if predicted_label != last_detected_label:
                print(f"Obiect nou detectat: {predicted_label} (incredere: {confidence:.2f}). Trimit imaginea la Gemini...")

                # Salvăm local pentru verificare vizuală (opțional)
                image_pil.save(f"captura_{predicted_label}.png")

                culoare = get_color_from_gemini(image_pil)
                print(f"Obiect: {predicted_label}, Culoare detectată de Gemini: {culoare}")

                # Construim textul cu diacritice pentru TTS
                text_de_spus = f"Am detectat {predicted_label} de culoare {culoare}."
                asyncio.run(speak(text_de_spus))

                last_detected_label = predicted_label
            else:
                print(f"Acelasi obiect detectat: {predicted_label} (ignorat pentru culoare)")
        else:
            print("Nimic detectat / Încredere prea mică")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Oprire program.")

finally:
    picam2.stop()
    print("Camera oprită.")

