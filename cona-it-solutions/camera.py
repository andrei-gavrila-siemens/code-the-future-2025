#!/usr/bin/env python3
import time
import requests
from picamera2 import Picamera2
from libcamera import controls
from io import BytesIO
from gpiozero import DistanceSensor

# Configurație
SERVER_URL = "https://fb3c-86-124-190-82.ngrok-free.app/process_image"  # Înlocuiește cu adresa corectă
CAPTURE_INTERVAL = 5  # secunde

# Configurare senzor distanță
ECHO_PIN = 17
TRIGGER_PIN = 4
MAX_DISTANCE = 0.4  # distanța maximă în metri pentru detecție
THRESHOLD_DISTANCE = 0.25  # distanța sub care obiectul este considerat detectat (în metri)

def setup_sensor():
    """Configurează senzorul ultrasonic"""
    print("Inițializare senzor ultrasonic...")
    # Specifică threshold_distance pentru a defini când un obiect este "în rază"
    sensor = DistanceSensor(
        echo=ECHO_PIN, 
        trigger=TRIGGER_PIN, 
        max_distance=MAX_DISTANCE,
        threshold_distance=THRESHOLD_DISTANCE
    )
    print(f"Senzor ultrasonic inițializat. Threshold: {THRESHOLD_DISTANCE}m")
    return sensor

def setup_camera():
    """Configurează camera cu Picamera2"""
    print("Configurare cameră cu Picamera2...")
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (640, 480)},
        buffer_count=2
    )
    picam2.configure(config)
    
    # Setări optime pentru Pi Zero
    picam2.set_controls({
        "AwbEnable": True,
        "AwbMode": controls.AwbModeEnum.Auto,
        "FrameRate": 15,
        "NoiseReductionMode": controls.draft.NoiseReductionModeEnum.HighQuality
    })
    
    return picam2

def capture_and_send(picam2):
    """Capturează imagine și o trimite la server"""
    try:
        # Captură imagine în memorie
        stream = BytesIO()
        picam2.capture_file(stream, format="jpeg")
        stream.seek(0)
        
        # Trimite la server
        files = {'image': ('cube.jpg', stream, 'image/jpeg')}
        response = requests.post(SERVER_URL, files=files, timeout=10)
        
        if response.status_code == 200:
            print("Imagine trimisă cu succes")
        else:
            print(f"Eroare server: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Eroare captură/trimitere: {str(e)}")
    finally:
        stream.close()

def main():
    print("Pornire script captură imagini (Picamera2)")
    
    try:
        # Inițializare senzor și cameră
        sensor = setup_sensor()
        picam2 = setup_camera()
        picam2.start()
        time.sleep(2)  # Încălzire camera
        
        print("Sistemul e pregătit. Așteptare detectare obiect...")
        
        while True:
            print("Aștept obiect în rază...")
            # Acest apel va bloca execuția până când un obiect intră în rază
            sensor.wait_for_in_range()
            time.sleep(0.5)
            print("Obiect detectat în rază!")
            print(f"Distanță actuală: {sensor.distance:.2f} metri")
            print(f"Captez imagine la {time.strftime('%H:%M:%S')}")
            
            # Captează și trimite imagine
            capture_and_send(picam2)
            
            # Așteaptă până când obiectul iese din rază
            print("Aștept ca obiectul să iasă din rază...")
            sensor.wait_for_out_of_range()
            print("Obiectul a ieșit din rază")
            
            # Așteaptă un interval minim între detecții consecutive
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Oprire script")
    except Exception as e:
        print(f"Eroare neașteptată: {str(e)}")
    finally:
        if 'picam2' in locals():
            picam2.stop()
        print("Camera oprită corect")

if _name_ == "_main_":
    main()