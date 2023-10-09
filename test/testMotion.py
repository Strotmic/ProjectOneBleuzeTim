
from RPi import GPIO
import time

pin = 21
# led= 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)
def call_method(pin):
    print('hey')
# GPIO.setup(led, GPIO.OUT)
GPIO.add_event_detect(pin, GPIO.RISING,
                      call_method, bouncetime=200)

try:
    while True:
        print('-'*40)
        test = GPIO.input(pin)

        print(test)
        time.sleep(0.1)
except KeyboardInterrupt as e:
    print(e)

finally:
    GPIO.cleanup()