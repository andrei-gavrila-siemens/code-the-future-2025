import RPi.GPIO as GPIO
import smbus
import time
import json
import threading
import paho.mqtt.client as mqtt
import os

# MQTT Settings
MQTT_BROKER = "172.31.99.35"  # Replace with your broker IP
MQTT_PORT = 1884
MQTT_TOPIC_JOYSTICK = "rpi0/joystick"
MQTT_TOPIC_SENSOR = "rpi0/mpu6050"
MQTT_TOPIC_TEMPERATURE = "rpi0/cpu_temp"

# Initialize MQTT Client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# --- JOYSTICK SETUP ---
joystick_pins = {
    "UP": 25, "DOWN": 24, "LEFT": 23, "RIGHT": 22,
    "BUTTON PRESSED": 27, "SET": 17, "RST": 4
}

GPIO.setmode(GPIO.BCM)
for pin in joystick_pins.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Debounce Variables
previous_states = {key: GPIO.HIGH for key in joystick_pins.keys()}
debounce_time = 0.2  # Debounce delay in seconds

# --- MPU6050 SETUP ---
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

bus = smbus.SMBus(1)
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

# Offset values (replace with your observed drift values)
ACCEL_X_OFFSET = 12664
ACCEL_Y_OFFSET = 4996
ACCEL_Z_OFFSET = 10600
GYRO_X_OFFSET = -150
GYRO_Y_OFFSET = 1570
GYRO_Z_OFFSET = -149

# Initialize storage for moving average filter
accel_x_data, accel_y_data, accel_z_data = [], [], []
gyro_x_data, gyro_y_data, gyro_z_data = [], [], []

# --- FUNCTION DEFINITIONS ---
def read_word(addr):
    """Reads 16-bit data from MPU6050"""
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) + low
    return value if value < 32768 else value - 65536

def moving_average(data, new_value, window_size=10):
    """Applies a simple moving average filter"""
    data.append(new_value)
    if len(data) > window_size:
        data.pop(0)
    return sum(data) / len(data)

def get_cpu_temp():
    """Read CPU temperature from system file."""
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.readline().strip()
    return float(temp) / 1000  # Convert from millidegrees to Celsius

def read_joystick():
    """Detect joystick movements and publish them to MQTT."""
    while True:
        for direction, pin in joystick_pins.items():
            current_state = GPIO.input(pin)

            if current_state == GPIO.LOW and previous_states[direction] == GPIO.HIGH:
                print(f"{direction} pressed!")
                client.publish(MQTT_TOPIC_JOYSTICK,json.dumps({"joystick": direction}))
                time.sleep(debounce_time)  # Debounce delay

            previous_states[direction] = current_state
        
        time.sleep(0.5)  # Prevent excessive CPU usage

def read_mpu6050():
    """Reads MPU6050 sensor data and sends it via MQTT."""
    while True:
        accel_x = moving_average(accel_x_data, read_word(ACCEL_XOUT_H) - ACCEL_X_OFFSET)
        accel_y = moving_average(accel_y_data, read_word(ACCEL_XOUT_H + 2) - ACCEL_Y_OFFSET)
        accel_z = moving_average(accel_z_data, read_word(ACCEL_XOUT_H + 4) - ACCEL_Z_OFFSET)

        gyro_x = moving_average(gyro_x_data, read_word(GYRO_XOUT_H) - GYRO_X_OFFSET)
        gyro_y = moving_average(gyro_y_data, read_word(GYRO_XOUT_H + 2) - GYRO_Y_OFFSET)
        gyro_z = moving_average(gyro_z_data, read_word(GYRO_XOUT_H + 4) - GYRO_Z_OFFSET)

        payload = {
            "accelerometer": {"x": round(accel_x, 2), "y": round(accel_y, 2), "z": round(accel_z, 2)},
            "gyroscope": {"x": round(gyro_x, 2), "y": round(gyro_y, 2), "z": round(gyro_z, 2)},
            "timestamp": time.time()
        }

        json_payload = json.dumps(payload)
        client.publish(MQTT_TOPIC_SENSOR, json_payload)
        print(f"Published Sensor Data: {json_payload}")

        time.sleep(1.5)
def monitor_cpu_temp():
    """Monitors CPU temperature and publishes to MQTT."""
    while True:
        cpu_temp = get_cpu_temp()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "timestamp": timestamp,
            "cpu_temperature": round(cpu_temp, 2)
        }

        json_payload = json.dumps(payload)
        client.publish(MQTT_TOPIC_TEMPERATURE, json_payload)
        print(f"Published CPU Temp: {json_payload}")
        
        time.sleep(30)  # Send data every 30 seconds

# --- MULTI-THREAD EXECUTION ---
try:
    # Create and start threads
    joystick_thread = threading.Thread(target=read_joystick, daemon=True)
    sensor_thread = threading.Thread(target=read_mpu6050, daemon=True)
    temp_thread = threading.Thread(target=monitor_cpu_temp, daemon=True)

    joystick_thread.start()
    sensor_thread.start()
    temp_thread.start()

    # Keep the main thread running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nShutting down...")
    GPIO.cleanup()
    client.disconnect()
