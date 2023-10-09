#!/usr/bin/python
import os, sys
import serial
import time

ser = serial.Serial('/dev/ttyUSB0',19200, timeout = 5)

# listen for the input, exit if nothing received in timeout period
while True:
    output = ''
    ser = serial.Serial('/dev/ttyUSB0', 9600, 8, 'N', 1, timeout=0.1)
    while output == '':
        output = ser.readline()
    print(output)
