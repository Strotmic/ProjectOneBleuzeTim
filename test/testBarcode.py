from RPi import _GPIO
import time
import serial

ser = serial.Serial("/dev/ttyS0")
# print(ser.name)

# ser.write(b'test')

try:
    while True:
        test = input('scan iets')
        print(test)

        
except KeyboardInterrupt as e:
    print(e)
finally:
    ser.close()

# import serial.tools.list_ports
# myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
# print(myports)


