import RPi.GPIO as GPIO
import time

# Configurează placa să folosească numerotarea BCM
GPIO.setmode(GPIO.BCM)

# Configurează GPIO 27 ca OUTPUT, cu pull-down activat
GPIO.setup(27, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)

# Trimite semnal HIGH (1)
print("🔧 Trimit semnal HIGH (1) pe GPIO 27...")
GPIO.output(27, GPIO.HIGH)

# Ține semnalul 2 secunde
time.sleep(10)

# Oprește semnalul (LOW)
GPIO.output(27, GPIO.LOW)
print("✅ Semnal LOW (0) trimis.")

# Curăță configurația GPIO
GPIO.cleanup()

