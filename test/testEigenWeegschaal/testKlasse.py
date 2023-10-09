from loadClass import HX711
import time
from RPi import GPIO
hx711 = HX711(dt=5, sck=6)
hx711.setup()

try:
    while True:
        print("ready")
        weight = hx711.get_weight()
        print("Weight: {} grams".format(weight))
        time.sleep(1)
except KeyboardInterrupt:
    pass

hx711.cleanup()
GPIO.cleanup()
