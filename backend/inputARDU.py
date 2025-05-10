import serial
import time
import serial.tools.list_ports

def trimiteComanda(cmd, port='/dev/ttyACM0', baudrate=9600):
    with serial.Serial(port, baudrate, timeout=1) as ser:
        time.sleep(2)
        ser.write(cmd.encode('utf-8'))


if __name__ == "__main__":
    for p in serial.tools.list_ports.comports():
        print(f"Port: {p.device}, Descriere: {p.description}")
    