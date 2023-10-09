import RPi.GPIO as GPIO

class HX711:
    def __init__(self, dt, sck):
        self.dt = dt
        self.sck = sck
        self.tare = 0

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dt, GPIO.IN)
        GPIO.setup(self.sck, GPIO.OUT)
        GPIO.output(self.sck, GPIO.LOW)
        self.tare = self.read()

    def wait(self):
        return GPIO.input(self.dt) == 0

    def read(self):
        while not self.wait():
            pass

        data = 0
        for i in range(24):
            GPIO.output(self.sck, GPIO.HIGH)
            data = (data << 1) | GPIO.input(self.dt)
            GPIO.output(self.sck, GPIO.LOW)

        GPIO.output(self.sck, GPIO.HIGH)
        data = data ^ 0b100000000000000000000000
        GPIO.output(self.sck, GPIO.LOW)

        data = data - self.tare

        return data

    def get_weight(self):
        raw_value = self.read()
        weight = raw_value / 209

        if weight > -3 and weight < 3:
            weight = 0

        return weight

    def cleanup(self):
        GPIO.cleanup([self.dt, self.sck])