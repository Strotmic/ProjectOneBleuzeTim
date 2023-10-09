from RPi import GPIO


class Pcf8574:
    def __init__(self, SDA, SCL, address=0x20):
        self.SDA = SDA
        self.SCL = SCL
        self.address = address & 0x7F
        self.__setup()
        self.dot = 0

    def __setup(self):
        GPIO.setmode(GPIO.BCM)
        for pin in [self.SDA, self.SCL]:
            GPIO.setup(pin, GPIO.OUT)

    def __start_conditie(self):
        # print("start")
        GPIO.output(self.SDA, GPIO.HIGH)
        GPIO.output(self.SCL, GPIO.HIGH)
        GPIO.output(self.SDA, GPIO.LOW)
        GPIO.output(self.SCL, GPIO.LOW)

    def __stop_conditie(self):
        # print("stop")
        GPIO.output(self.SDA, GPIO.LOW)
        GPIO.output(self.SCL, GPIO.LOW)
        GPIO.output(self.SCL, GPIO.HIGH)
        GPIO.output(self.SDA, GPIO.HIGH)

    def __writebit(self, bit):
        GPIO.output(self.SDA, bit)
        GPIO.output(self.SCL, GPIO.HIGH)
        GPIO.output(self.SCL, GPIO.LOW)
        GPIO.output(self.SDA, GPIO.LOW)

    def __ack(self):
        GPIO.setup(self.SDA, GPIO.IN, GPIO.PUD_UP)
        GPIO.output(self.SCL, GPIO.HIGH)
        ackbit = GPIO.input(self.SDA)
        GPIO.setup(self.SDA, GPIO.OUT)
        GPIO.output(self.SCL, GPIO.LOW)
        # print("ack {0}".format(ackbit))
        if ackbit:
            print("verkeerd adres!")
            return False
        else:
            return True

    def __writebyte(self, byte):
        # print("writebyte : {}".format(byte))
        mask = 0x80
        for i in range(0, 8):
            # bit = byte & mask
            # writebit(bit)
            # mask >>= 1
            # print(bit)
            if byte & mask > 0:
                self.__writebit(True)
            else:
                self.__writebit(False)
            mask >>= 1

    def write_outputs(self, data: int):
        address_write = self.address << 1
        data = (data & 0xFF) | self.dot
        self.__start_conditie()
        self.__writebyte(address_write)
        self.__ack()
        self.__writebyte(data)
        self.__ack()
        self.__stop_conditie()

