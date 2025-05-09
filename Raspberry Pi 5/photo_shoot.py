from picamera2 import Picamera2, Preview
import time

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

picam2.configure(picam2.preview_configuration)
picam2.start()

time.sleep(10)

picam2.stop_preview()
picam2.stop()

