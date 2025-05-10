import time
import sys
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from picamera2 import Picamera2
import datetime

# Try to import serial but skip if not connected
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# Initialize serial
def init_serial(port='/dev/ttyACM0', baudrate=9600):
    if not SERIAL_AVAILABLE:
        print("PySerial not available, skipping serial connection.")
        return None

    try:
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        print(f"Serial connected to {port}")
        return ser
    except serial.SerialException as e:
        print(f"Warning: Couldn't connect to serial: {e}")
        print("Continuing without serial connection.")
        return None

# Send command to Arduino (or just print if no serial)
def send_command(ser, command):
    if ser:
        ser.write((command + '\n').encode('utf-8'))
        print(f"Sent to Arduino: {command}")
    else:
        print(f"(No serial) Would send: {command}")

# Record video (1 minute)
def record_video(duration=60, plant_name="Unnamed Plant"):
    picam2 = Picamera2()
    config = picam2.create_video_configuration()
    picam2.configure(config)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"watering_{plant_name}_{timestamp}.h264"

    encoder = H264Encoder()
    output = FileOutput(filename)

    picam2.start_recording(encoder, output)
    print(f"Recording started: {filename}")

    time.sleep(duration)

    picam2.stop_recording()
    print("Recording stopped.")
    picam2.close()  # Release the camera


# Take a photo
def take_photo(plant_name="Unnamed Plant"):
    picam2 = Picamera2()
    config = picam2.create_still_configuration()
    picam2.configure(config)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{plant_name}_Pic_{timestamp}.jpg"
    picam2.start()
    time.sleep(2)  # Camera warm-up
    picam2.capture_file(filename)
    picam2.stop()
    print(f"Photo taken: {filename}")
    picam2.close()  # Release the camera

# Read plant name from file (if exists)
def read_plant_name():
    try:
        with open("plant_name.txt", "r") as file:
            plant_name = file.read().strip()
            if not plant_name:
                plant_name = "Unnamed Plant"
            return plant_name
    except FileNotFoundError:
        return "Unnamed Plant"

# Write plant name to file
def write_plant_name(plant_name):
    with open("plant_name.txt", "w") as file:
        file.write(plant_name)

# Name the plant
def name_plant():
    global plant_name
    print(f"Current plant name is '{plant_name}'.")
    plant_name = input("Enter a new name or press Enter to keep it: ").strip()
    if not plant_name:
        print("Plant name not changed.")
    else:
        write_plant_name(plant_name)
        print(f"Plant name changed to '{plant_name}'.")

# Menu system
def main():
    global plant_name
    plant_name = read_plant_name()  # Load the plant name from file
    ser = init_serial()

    while True:
        print("\n=== Plant Watering Robot Menu ===")
        print("1. Water the plant WITH video")
        print("2. Water the plant WITHOUT video")
        print("3. Take a picture of the arm and plant")
        print("4. Name or change the plant name")
        print("5. Exit")

        choice = input("Select an option (1-5): ").strip()
        
        if choice == '1':
            send_command(ser, "WATER")
            print("Watering the plant WITH video...")
            record_video(plant_name=plant_name)
        elif choice == '2':
            send_command(ser, "WATER")
            print("Watering the plant WITHOUT video... Please wait 30 seconds.")
            time.sleep(30)
            print("Watering finished.")
        elif choice == '3':
            print("Taking a picture...")
            take_photo(plant_name=plant_name)
        elif choice == '4':
            name_plant()
        elif choice == '5':
            print("Exiting program.")
            if ser:
                ser.close()
            break
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == '__main__':
    main()
