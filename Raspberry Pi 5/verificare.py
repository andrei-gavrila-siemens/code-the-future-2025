import os
import time
import numpy as np
import tensorflow as tf
from PIL import Image
from picamera2 import Picamera2
import io
import google.generativeai as genai
import RPi.GPIO as GPIO
import asyncio
from dotenv import load_dotenv
from stt import listen_background
from tts import speak

# Configurare GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)  # Pinul care trimite start brațului robotic
GPIO.output(27, GPIO.HIGH)

# Încarcă cheia API Google
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY lipsește. Verifică fișierul .env.")

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
            "Spune doar ce culoare are obiectul din imagine. "
            "Răspunde doar cu un singur cuvânt: roșu, albastru, verde, galben, portocaliu, mov, maro, negru, alb, gri, roz, turcoaz."
        )
        response = model.generate_content(
            [
                prompt,
                {
                    "mime_type": "image/png",
                    "data": image_bytes
                }
            ],
            generation_config=genai.types.GenerationConfig(max_output_tokens=10)
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

last_detected_label = None
activ = False

# Callback pentru STT
def on_command(text):
    global activ
    if "start" in text:
        print("Comanda 'start' detectată!")
        activ = True

# Pornește ascultarea în fundal
listen_background(on_command)

print("Sistem pornit. Aștept comanda 'start'...")

async def main_loop():
    global activ, last_detected_label
    try:
        while True:
            if activ:
                picam2.start()
                print("Detectez obiecte noi...")

                while activ:
                    frame = picam2.capture_array()
                    image_pil = Image.fromarray(frame, 'RGB')

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
                            print(f"Obiect nou detectat: {predicted_label}")
                            culoare = get_color_from_gemini(image_pil)
                            print(f"Culoarea obiectului: {culoare}")

                            mesaj = f"Obiectul identificat este: {predicted_label} și are culoarea {culoare}."
                            await speak(mesaj)

                            # Trimite semnal de start brațului robotic (puls GPIO 27)
                            GPIO.output(27, GPIO.LOW)
                            print("✅ Semnal de START trimis către brațul robotic.")
                            await asyncio.sleep(2)  # ține semnalul 2 secunde
                            GPIO.output(27, GPIO.HIGH)
                            print("⏹ Semnal oprit.")

                            last_detected_label = predicted_label

                    await asyncio.sleep(0.5)
            else:
                await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Oprire program.")
    finally:
        picam2.stop()
        GPIO.output(27, GPIO.HIGH)
        GPIO.cleanup()
        print("Camera și GPIO oprite.")

if __name__ == "__main__":
    asyncio.run(main_loop())

