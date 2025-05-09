import smbus
import time
import json
import paho.mqtt.client as mqtt

# MQTT Settings
MQTT_BROKER = "192.168.43.236"
MQTT_PORT = 1884
MQTT_TOPIC = "rpi0/mpu6050"

# Initialize MQTT Client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# MPU6050 Registers
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

bus = smbus.SMBus(1)
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

def read_word(addr):
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) + low
    return value if value < 32768 else value - 65536

def moving_average(data, new_value, window_size=10):
    data.append(new_value)
    if len(data) > window_size:
        data.pop(0)
    return sum(data) / len(data)

# Drift values
ACCEL_X_OFFSET = 12664
ACCEL_Y_OFFSET = 4996
ACCEL_Z_OFFSET = 10600
GYRO_X_OFFSET = -150
GYRO_Y_OFFSET = 1570
GYRO_Z_OFFSET = -149

# Initialize storage for moving average filter
accel_x_data, accel_y_data, accel_z_data = [], [], []
gyro_x_data, gyro_y_data, gyro_z_data = [], [], []

while True:
    accel_x = moving_average(accel_x_data, read_word(ACCEL_XOUT_H) - ACCEL_X_OFFSET)
    accel_y = moving_average(accel_y_data, read_word(ACCEL_XOUT_H + 2) - ACCEL_Y_OFFSET)
    accel_z = moving_average(accel_z_data, read_word(ACCEL_XOUT_H + 4) - ACCEL_Z_OFFSET)

    gyro_x = moving_average(gyro_x_data, read_word(GYRO_XOUT_H) - GYRO_X_OFFSET)
    gyro_y = moving_average(gyro_y_data, read_word(GYRO_XOUT_H + 2) - GYRO_Y_OFFSET)
    gyro_z = moving_average(gyro_z_data, read_word(GYRO_XOUT_H + 4) - GYRO_Z_OFFSET)

    # Create JSON payload
    payload = {
        "accelerometer": {"x": round(accel_x, 2), "y": round(accel_y, 2), "z": round(accel_z, 2)},
        "gyroscope": {"x": round(gyro_x, 2), "y": round(gyro_y, 2), "z": round(gyro_z, 2)},
        "timestamp": time.time()
    }

    json_payload = json.dumps(payload)

    # Publish data to MQTT broker
    client.publish(MQTT_TOPIC, json_payload)
    print(f"Published: {json_payload}")

    time.sleep(1)