from RPi import GPIO
import serial
from spi import mcp
import time
from datetime import datetime
from subprocess import check_output

# i2c = SMBus()
# i2c.open(1)
# # i2c.write_byte(0x20,0xFF)

'''
Declaratie van variabels
'''
ser = serial.Serial('/dev/ttyAMA0')

btn = 21
value = 1
prevX = 0
prevY = 0

a = 1

display = LCD(26, 20, i3c)
Spi = mcp(0, 0)

rood = 12
blauw = 19
groen = 13

current_time = datetime.now().strftime("%H:%M")
ser.write(current_time.encode(encoding='utf-8'))
prevTime = int(current_time[-1:])
seconds = 0
btnseconden = 27
startSeconden = 0

'''
GPIO setups = 
'''

GPIO.setmode(GPIO.BCM)

GPIO.setup(btn, GPIO.IN)
GPIO.setup(btnseconden, GPIO.IN)
# GPIO.setup(rs, GPIO.OUT)
# GPIO.setup(e, GPIO.OUT)

GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btnseconden, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(rood, GPIO.OUT)
GPIO.setup(groen, GPIO.OUT)
GPIO.setup(blauw, GPIO.OUT)
rood_pwm = GPIO.PWM(rood, 1000)
blauw_pwm = GPIO.PWM(blauw, 1000)
groen_pwm = GPIO.PWM(groen, 1000)

'''
defenitions
'''


def count(x):
    global value
    global a
    value = 1
    a += 1
    if a == 4:
        a = 1


def seconden(x):
    global startSeconden
    global seconds
    startSeconden = time.time()
    second = str(datetime.now())[-9:-7]
    ser.write(second.encode(encoding='utf-8'))
    seconds = 1


'''
Events
'''

GPIO.add_event_detect(btn, GPIO.FALLING, callback=count, bouncetime=200)
GPIO.add_event_detect(btnseconden, GPIO.FALLING,
                      callback=seconden, bouncetime=200)

'''
Code
'''

ips = str(check_output(['ifconfig', 'wlan0']))
startpos = ips.find("inet")+4
ips = ips[startpos:].split(" ")
ips = ips[1]

try:
    rood_pwm.start(0)
    groen_pwm.start(0)
    blauw_pwm.start(0)
    while True:
        current_time = datetime.now().strftime("%H:%M")
        valX = Spi.b_in(1)
        valY = Spi.b_in(0)
        '''
        Checkup van tijd voor door te sturen naar arduino
        '''
        if startSeconden + 6.5 < time.time() and seconds == 1:
            seconds = 0
            ser.write(current_time.encode(encoding='utf-8'))

        if (int(current_time[-1:]) != prevTime) and seconds == 0:
            ser.write(current_time.encode(encoding='utf-8'))

        prevTime = int(current_time[-1:])

        '''
        Checkup van status voor lcd
        '''
        if a == 1 and value == 1:
            display.cmd_clear_display()
            display.write_message('WLAN0')
            
            display.write_message(f'{ips}')
            value += 1

        if a == 2 and (value == 1 or prevX-3 <= valX >= prevX+3):
            display.cmd_clear_display()
            display.write_message(f'value x {valX}')
            display.cmd_set_cursor(1, 0)
            value += 1

        if a == 3 and (value == 1 or prevY-3 <= valY >= prevX+3):
            display.cmd_clear_display()
            display.write_message(f'value y {valY}')
            display.cmd_set_cursor(1, 0)
            value += 1

        '''
        instellen van pwm voor de rgb led
        '''
        prevX = valX
        prevY = valY
        rood_pwm.ChangeDutyCycle((valX/1023)*100)
        blauw_pwm.ChangeDutyCycle((valY/1023)*100)
        blauw_pwm.ChangeDutyCycle((((valY+valX)/2)/1023)*100)
        time.sleep(0.01)

except KeyboardInterrupt as e:
    print(e)

finally:
    rood_pwm.stop()
    blauw_pwm.stop()
    groen_pwm.stop()
    ser.close()
    GPIO.cleanup()
    Spi.close()
