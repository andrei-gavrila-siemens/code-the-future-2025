import paho.mqtt.client as mqtt
import time
import os
from picamera2 import Picamera2

broker = "192.168.43.236"
port = 1884 
topic = "camera/capture"

picam2 = Picamera2()
picam2.start_preview()

picam2.configure(picam2.create_preview_configuration())
picam2.start()
print("Camera preview started. Press Enter to capture an image...")

client = mqtt.Client()
client.connect(broker, port, 60)
client.loop_start()

# Wait for the user to press Enter
input("Press Enter to capture an image...")
input()
timestamp = int(time.time())
filename = f"image_{timestamp}.jpg"
picam2.capture_file(filename)
print(f"Image saved as {filename}")

# Wait for the image to be saved
image_url = f"http://{broker}:8000/{filename}"
client.publish(topic, image_url)
print(f"Published image URL: {image_url}")

# Clean up
picam2.stop()
client.loop_stop()
client.disconnect()