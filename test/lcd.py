from RPi import GPIO
import time


class LCD:
    def __init__(self, rs, e, pcf):
        self.rs = rs
        self.e = e
        self.pcf = pcf

        GPIO.setup(self.rs, GPIO.OUT)
        GPIO.setup(self.e, GPIO.OUT)

        self._setup()

    '''
    WRITE defs
    '''

    def write_message(self, message):
        for i in message[:16]:
            self.write_character(ord(i))
        for i in message[16:]:
            self.cmd_move_screen()
            self.write_character(ord(i))

    def write_character(self, x):
        GPIO.output(self.rs, GPIO.HIGH)
        GPIO.output(self.e, GPIO.HIGH)

        self.send_data_bits(x)
        GPIO.output(self.e, GPIO.LOW)
        time.sleep(0.05)

    '''
    Command defs
    '''

    def cmd_clear_display(self):
        self.send_instruction(0b00000001)

    def cmd_move_screen(self):
        self.send_instruction(0b00011000)

    def cmd_set_cursor(self, r, c):
        byte = r << 6 | c
        self.send_instruction(byte | 128)

    '''
    SETUP
    '''

    def _setup(self):
        self.send_instruction(0b00111000)
        self.send_instruction(0b00001111)
        self.cmd_clear_display()

    '''
    Instrusctions + data
    '''

    def send_instruction(self, x):
        GPIO.output(self.rs, GPIO.LOW)
        GPIO.output(self.e, GPIO.HIGH)
        self.send_data_bits(x)
        GPIO.output(self.e, GPIO.LOW)
        time.sleep(0.05)

    def send_data_bits(self, b):
        self.pcf.write_outputs(b)
