from picamera2 import Picamera2
import numpy as np
import tensorflow as tf
import time
from PIL import Image

# Incarca modelul floating point si etichetele
interpreter = tf.lite.Interpreter(model_path="model_unquant.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

with open('labels.txt', 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Prag de incredere minim (ajustabil)
threshold = 0.7  # minim 80%

# Initializeaza camera
picam2 = Picamera2()
picam2.configure(picam2.preview_configuration)
picam2.start()

print("Pornit. Apasa Ctrl+C pentru a iesi.")

try:
    while True:
        # Captureaza frame ca array
        frame = picam2.capture_array()

        # Converteste frame-ul in imagine PIL, converteste in RGB si redimensioneaza
        image_pil = Image.fromarray(frame).convert("RGB")
        image_pil = image_pil.resize((224, 224))
        img = np.array(image_pil)

        # Pregateste inputul (normalizare intre 0 si 1)
        img = np.expand_dims(img, axis=0).astype(np.float32) / 255.0

        # Ruleaza predictia
        interpreter.set_tensor(input_details[0]['index'], img)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])[0]

        predicted_index = np.argmax(output_data)
        predicted_label = labels[predicted_index]
        confidence = output_data[predicted_index]

        if confidence >= threshold:
            print(f"Detectat: {predicted_label} (incredere: {confidence:.2f})")
        else:
            print("Nimic detectat / incredere prea mica")

        time.sleep(1.5)  # pauza mica intre cadre

except KeyboardInterrupt:
    print("Oprire program.")

finally:
    picam2.stop()

