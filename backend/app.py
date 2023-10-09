import threading
import time
from datetime import datetime
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from RPi import GPIO
from lcd import lcd
from hx711 import HX711
import os
import re
from pcf import Pcf8574
from helpers.klasseknop import Button
import board
import neopixel
import serial
# import repositories.adafruit_fingerprintClass as adafruit_fingerprint
import adafruit_fingerprint
from repositories.DataRepository import DataRepository
import json
from subprocess import check_output

'''
NEOPIXEL
'''

uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

array = []


# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 24

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

'''
Ip-adressen
'''
ips = str(check_output(['ifconfig', 'wlan0']))
startpos = ips.find("inet")+4
ips = ips[startpos:].split(" ")
ips = ips[1]


# from fingerprint_simpletest_rpi import get_fingerprint
app = Flask(__name__)
app.config['SECRET_KEY'] = 'HELLOTHISISSCERET'

socketio = SocketIO(app, cors_allowed_origins="*",
                    async_mode='gevent', ping_interval=0.5)
CORS(app)

endpoint = '/api/v1'
GPIO.setmode(GPIO.BCM)
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(435)
hx.reset()
hx.tare()

motion_pin=21
pin = 20
display = lcd()

GPIO.setup(motion_pin, GPIO.IN, GPIO.PUD_UP)
btn = Button(pin)

def callback(pin):
    weeg('test')

# def motion_callback(pin):
#     global start_motion
#     start_motion = time.time()
#     print(start_motion)
#     print('motion aan')
#     DataRepository.add_meting(4,5,'AAN','motion sensor gaat aan')


def enroll_save_to_file(userID):
    """Take a 2 finger images and template it, then store it in a file"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print('place finger')
            display.lcd_clear()
            display.print("Place finger on sensor...")
        else:
            print('place same finger')

            display.lcd_clear()
            display.print("Place same finger again...")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                display.lcd_clear()
                display.print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                display.lcd_clear()
                display.print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()
    display.lcd_clear()
    display.print("Creating model...")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            display.lcd_clear()
            print('no match')
            display.print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Downloading template...")
    data = finger.get_fpdata("char", 1)
    DataRepository.add_fingerprint(userID, str(data))
    display.lcd_clear()
    display.print("Template is saved in template0.dat file.")

    return True

def fingerprint_check_file():
    """Compares a new fingerprint template to an existing template stored in a file
    This is useful when templates are stored centrally (i.e. in a database)"""
    print("Waiting for finger print...")
    start = time.time()
    print(start)
    while (finger.get_image() != adafruit_fingerprint.OK):
        if start+3<time.time():
            break
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False

    print("Loading file template...", end="")
    data = DataRepository.get_all_fingerprints()
    print(f'Dit is de lengte {len(data)}')
    # print(data)
    for x in data:
        data = (x['fingerScan'])
        # print(data)
        print('-'*40)
        print(f"Dit is de fingerscn {x['fingerScan']}")
        if x['fingerScan']==None:
            continue
        try:
            data = json.loads(data)

            finger.send_fpdata((data), "char", 2)

            i = finger.compare_templates()
            if i == adafruit_fingerprint.OK:
                print("Fingerprint match template in file.")
                print(x['userID'])
                return [True, x['userID']]
            if i == adafruit_fingerprint.NOMATCH:
                print("Templates do not match!")

            else:
                print("Other error!")
        except:
            return False
    return False

# btn.on_press(callback)
# GPIO.add_event_detect(motion_pin, GPIO.RISING,
#                       motion_callback, bouncetime=200)

'''
FOOD
'''

@app.route(endpoint + '/foodTable/', methods=['GET', 'POST'])
def get_food_table():
    print(request.method)
    if request.method == 'GET':
        x=DataRepository.get_food_table()
        return jsonify(x), 200
    elif request.method=='POST':

        input= DataRepository.json_or_formdata(request)
        print(input)
        data = DataRepository.add_food(input['name'],input['barcode'],input['categorie'],input['serving'],input['portionServing'],input['kcal'],input['saturated'],input['unsaturated'],input['protein'],input['carbo'],input['fiber'],input['sugar'],input['salt'])
        print(data)
        if data != None:
            print(data)
            return jsonify(foodID=data), 201
        else:
            return jsonify(message='errpr'), 500
@app.route(endpoint + '/foodTable/<categorieID>/', methods=['GET'])
def get_food_by_categorie_table(categorieID):
    if request.method == 'GET':
        x=DataRepository.get_food_by_categorie(categorieID)
        return jsonify(x), 200

@app.route(endpoint +'/goal/<userID>/', methods=['GET','POST'])
def change_goal(userID):
    print('test')
    if request.method=='GET':
        x = DataRepository.get_goal(userID)
        print(x)
        return jsonify(x), 201
    elif request.method=='POST':
        input = DataRepository.json_or_formdata(request)
        print(f'Dit si een test vna goal {input}')
        input=input
        data = DataRepository.set_goal(int(userID),input['dailyGoal'],input
        ['goalAmount'],'description')
        DataRepository.set_kleur(userID,input['kleur'][1:])
        print('change goal de data:')
        print(data)
        if data != None:
            print(data)
            return jsonify(foodID=data), 201
        else:
            return jsonify(message='errpr'), 500


@app.route(endpoint +'/foodCategories/', methods = ['GET'])
def get_food_categories():
    if request.method == 'GET':
        x = DataRepository.get_food_categories()
        return jsonify(x), 200
    
@app.route(endpoint + '/foodDetail/<foodID>/', methods=['GET'])
def get_food_detail(foodID):
    if request.method=='GET':
        data=DataRepository.get_detail_food(foodID)
        return jsonify(data), 200


'''
USER
'''
@app.route(endpoint + '/dailyGoal/<userID>/', methods=['GET'])
def get_daily_goal(userID):
    if request.method == 'GET':
        # data= DataRepository.get_daily_from_user(userID)
        # # {'Kcal': 1700.0, 'Protein': 3.7799999713897705, 'Fiber': 8.200000286102295, 'Salt': 1.8000000715255737, 'Saturated fat': 0.08400000259280205, 'Unsaturated fat': 0.0, 'Carbo Hydrates': 74.4300012588501, 'Sugar': 31.17000102996826}
        # print(data)
        # data = DataRepository.get_all_food_user_daily(userID)
        # print(data)
        # # for i in data:
        data = DataRepository.get_all_food_user_daily(userID)
        # print(data)
        l = {'Kcal':0, 'Protein':0, 'Fiber':0,'Salt':0,'Saturated fat':0,'Unsaturated fat':0,'Carbo Hydrates':0,'Sugar':0}
        try:
            for i in data:
                if i['serving']=='g':
                    qu=float(i['weight'])/float(i['portionServing'])
                    l['Kcal']+=i['kcal']*qu
                    l['Protein']+=i['protein']*qu
                    l['Fiber']+=i['fiber']*qu
                    l['Salt']+=i['salt']*qu
                    l['Saturated fat']=i['saturatedFat']*qu
                    l['Unsaturated fat']+=i['unsaturatedFat']*qu
                    l['Carbo Hydrates']+=i['carboHydrates']*qu
                    l['Sugar']+=i['sugar']*qu
                else:
                    l['Kcal'] += i['kcal']
                    l['Protein'] += i['protein']
                    l['Fiber'] += i['fiber']
                    l['Salt'] += i['salt']
                    l['Saturated fat'] = i['saturatedFat']
                    l['Unsaturated fat'] += i['unsaturatedFat']
                    l['Carbo Hydrates'] += i['carboHydrates']
                    l['Sugar'] += i['sugar']
            # return jsonify(data=data), 200
            print(l)
            socketio.emit('B2F_new_pie',data=l)
            return jsonify(data=l),200
        except:
            return jsonify(data=l), 200

@app.route(endpoint + '/historyGoal/<userID>/', methods=['GET'])
def get_history_goal_by_user(userID):
    if request.method=='GET':
        data = DataRepository.get_history_by_goal(userID)
        goal = DataRepository.get_goal(userID)
        print(data)
        print(goal)
        f = goal[0]['goal']
        print(f)
        l = []
        dates = []
        for i in data:
            if i['serving'] == 'g' and i['datum'].year==2023:
                qu = float(i['weight'])/float(i['portionServing'])
                if i['datum'] not in dates:
                    l.append({f: i[f]
                             * qu, 'datum': i['datum']})
                    dates.append(i['datum'])
                else:
                    place = dates.index(i['datum'])
                    l[place][f] += i[f]*qu
            elif i['datum'].year == 2023:
                if i['datum'] not in dates:
                    l.append({f: i[f], 'datum': i['datum']})
                    dates.append(i['datum'])
                else:
                    place = dates.index(i['datum'])
                    l[place][f] += i[f]

        return jsonify(l), 200

'''
THREADING
'''

def test():
    start = time.time()
    global start_motion
    start_motion = time.time()
    global login
    global userID
    login=0
    x=None
    userID=0
    while True:
        while login==0:
            black()
            try:
                x=False
                while x== False:
                    x = fingerprint_check_file()
                    print(login)
                    if login==1:
                        login = 1
                        x=[True]
                        break
                    elif login==-1:
                        while login==-1:
                            time.sleep(1)
                            print('Huidig registreren')
            except:
                print('except an lijn 366')

            if login==1:
                break
            print(f'lijn 375 {x}')
            if x==False:
                x=[False,0]
            if x[0]:
                # print('oke')
                login=1
                userID = x[1]
                DataRepository.add_meting(1,1,'LOGIN',f'de user met id {x[1]}logt in')
                socketio.emit('B2F_login', {'userID': x[1]})
                display.lcd_clear()
                display.print('Welkom')
                start_motion = time.time()
                start_neopixel()
            else:
                print('niet oke')
                login=0
            print("----------------**")
        # print('USERID:')
        # print(userID)
        # print(f' test op 391 {start_motion}')

        motion_sensor = GPIO.input(motion_pin)
        # print(motion_sensor)
        if motion_sensor ==1:
            start_motion = time.time()
        if start_motion+100<time.time():
            print(f'lijn 394 motion is te lang afgebleven')
            login=0
            socketio.emit('B2F_logout')
        time.sleep(0.5)

def neopixel_thread():
    global userID
    start =time.time()
    while True:   
        if start+3<time.time():
            # print('test')
            rainbow_cycle(1, userID)
            start=time.time()
            # time.sleep(1)

# def thread2():
    

def start_thread():
    # threading.Timer(10, all_out).start()
    t = threading.Thread(target=test, daemon=True)
    t.start()
    print("thread started")

def start_neopixel():
    t = threading.Thread(target=neopixel_thread, daemon=True)
    t.start()
'''
Gewicht Test
'''

def wegen(gewicht):
    if gewicht > 0:
        x = hx.get_weight(5)
        y = x-gewicht
        gewicht += y
        if y < 0:
            y = hx.get_weight(5)
            gewicht = y
        return [y, gewicht]

    else:
        x = hx.get_weight(5)
        gewicht += x
        return [x, gewicht]

'''
CODE VAN DE NEOXPIXEL HIERONDER
'''
def wheel2(pos):    
    r=0
    g=0
    b=0
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b)


def black():
    wait=0.01
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel2(pixel_index & 255)
        pixels.show()

def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def wheel(pos,userID):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
    # print(f'Lijn 436 {userID}')
    kleur = hex_to_rgb(DataRepository.get_kleur(userID)['kleur'])
    # print(kleur)
    if kleur==None:
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
    else:
        r=kleur[0]
        g=kleur[1]
        b=kleur[2]
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

global goalPrev
goalPrev=0

def rainbow_cycle(wait, userID):
    current = 0
    global goalPrev
    try:
        huidig = DataRepository.get_goal_by_user(userID)
        # print(huidig)
        goal = DataRepository.get_goal(userID)
    except:
        print('huidig of goel niet gelukt')
        huidig=0 
        goal=1
    # print('Neopixel TEST')
    # print(userID)
    # print(goal)
    # print(huidig)
    # print(goal)
    # print('STOP Neopixel TEST')
    goal = goal[0]['goalAmount']
    if goal!=goalPrev:
        black()
    goalPrev = goal
    if huidig==0:
        num_pixels=24
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255, userID)
            pixels.show()
    else:
        for i in huidig:
            if i['serving'] == 'g':
                    qu = float(i['weight'])/float(i['portionServing'])
                    current+=i['goal']*qu
            else:
                    current += i['goal']
        print(f'Test neopixel lijn 526: {current} {goal}')
        percent = current / goal
        num_pixels = round(percent*24)
        if num_pixels>24:
            num_pixels=24
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255, userID)
            pixels.show()

''''
SOCKET IO
'''
@socketio.on('F2B_voegToe')
def voegToe(x):
    print(x)

@socketio.on('F2B_poweroff')
def poweroff():
    os.system("shutdown now -h")

@socketio.on('F2B_tare')
def tare():
    global tare
    gewicht = round(hx.get_weight(5),2)
    tare=gewicht    
    print(tare)

def wegen_thread():
    global tare
    global gewicht
    global magwegen
    magwegen=1
    tare =0 
    gewichtprev = 0
    prevTare=0
    while True:
        while magwegen==1:
            gewicht = round(hx.get_weight(5),2)
            gewicht = round(gewicht - tare,2)
            if gewicht<0:
                gewicht =0
            display.lcd_clear()
            display.print(str(gewicht))
            time.sleep(1.5)
        while magwegen==0:
            time.sleep(0.5)

@socketio.on('F2B_start_wegen')
def start_wegen():
    print('test')
    t = threading.Thread(target=wegen_thread, daemon=True)
    t.start()

@socketio.on('F2B_histogram_pie')
def histogram(x):
    y=x[1]
    x=x[0]
    date_string = x.replace('GMT','')
    userID=y

    # print(date_string)
    datetime_object = datetime.strptime(
        date_string, '%a, %d %b %Y %H:%M:%S ').strftime("%Y-%m-%d")

    # print(datetime_object)

    data=DataRepository.get_all_food_user_daily(userID,datetime_object)
    l = {'Kcal':0, 'Protein':0, 'Fiber':0,'Salt':0,'Saturated fat':0,'Unsaturated fat':0,'Carbo Hydrates':0,'Sugar':0}
    for i in data:
            if i['serving']=='g':
                qu=float(i['weight'])/float(i['portionServing'])
                l['Kcal']+=i['kcal']*qu
                l['Protein']+=i['protein']*qu
                l['Fiber']+=i['fiber']*qu
                l['Salt']+=i['salt']*qu
                l['Saturated fat']=i['saturatedFat']*qu
                l['Unsaturated fat']+=i['unsaturatedFat']*qu
                l['Carbo Hydrates']+=i['carboHydrates']*qu
                l['Sugar']+=i['sugar']*qu
            else:
                l['Kcal'] += i['kcal']
                l['Protein'] += i['protein']
                l['Fiber'] += i['fiber']
                l['Salt'] += i['salt']
                l['Saturated fat'] = i['saturatedFat']
                l['Unsaturated fat'] += i['unsaturatedFat']
                l['Carbo Hydrates'] += i['carboHydrates']
                l['Sugar'] += i['sugar']
            # return jsonify(data=data), 200
    # print(l)
    socketio.emit('B2F_new_pie',data=l)


@socketio.on('F2B_login')
def login(x):
    global login
    global userID
    # print(x)
    y=(DataRepository.get_emails())
    for i in y:
        if x['email']==i['eMail']:
            # print('oke')
            login=1
            userID = i['userID']
            DataRepository.add_meting(1,1,'LOGIN',f'de user met id {userID}logt in')
            socketio.emit('B2F_login', {'userID': userID})
            display.lcd_clear()
            display.print('Welkom')
            break
    if login==0:
        print('email nt found')
        display.lcd_clear()
        display.print('email not found')

@socketio.on('F2B_logout')
def logout(x):
    global login
    black()
    login=0

# @socketio.on('F2B_weging')
# def add_food_gewicht(data):
#     print(l)
#     print(data)
#     DataRepository.add_food_to_meal(int(data[1]),int(data[0]), float(l[1]))
@socketio.on('F2B_login_uit')
def login_uit():
    global login
    login = -1
    print(login)

@socketio.on('F2B_register')
def register(x):
    global login
    login=-1
    print(x)
    goalID = DataRepository.add_goal(x['dailyGoal'],x['amount'])
    print(goalID)
    userID = DataRepository.add_user(x['voornaam'],x['naam'],x['email'],goalID,x['color'][1:])
    display.lcd_clear()
    display.print('Leg vinger op de scanner')
    time.sleep(5)
    print(test)
    if enroll_save_to_file(userID):
        login = 1
        DataRepository.add_meting(1,1,'LOGIN',f'de user met id {userID}logt in')
        socketio.emit('B2F_login', {'userID': userID})
        display.lcd_clear()
        login=1
        display.print('Welkom')



@socketio.on('F2B_barcode')
def barcode_scanner(l):
    print('De barcode is geenter')
    code = input('>>')
    print(code)
    print(l)
    try:
        x=DataRepository.get_food_by_barcode(code)
        y = DataRepository.add_food_to_meal(int(l[0]),x['foodID'],100)
        print(f'Test van barcoe op lijn 664: {y}')
        if type(y)==type(1):
            socketio.emit('B2F_barcode_succes',True)
    except:
        print('barcode niet gevodnden')
    


# API ENDPOINTS
@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # # Send to the client!
    # vraag de status op van de lampen uit de DB
    # status = DataRepository.read_status_lampen()
    # socketio.emit('B2F_status_lampen', {'lampen': status})
    # Beter is het om enkel naar de client te sturen die de verbinding heeft gemaakt.
    # emit('B2F_status_lampen', {'lampen': status}, broadcast=False)
    
global gewicht 
gewicht=0

@socketio.on('F2B_add_food')
def add_food(lijst):
    global gewicht
    global magwegen
    print(lijst)
    foodID = int(lijst[0])
    userID = int(lijst[1])
    print(userID)
    if(len(lijst)==3):
        gewicht=0
    print(lijst)
    magwegen=0
    DataRepository.add_food_to_meal(userID, foodID, gewicht)


@socketio.on('F2B_wegen')
def weeg(data):
        global gewicht 
        print(data)
        l = wegen(gewicht)
        l[0] = round(l[0],2)
        print(l[0])
        gewicht=l[1]
        if l[0] <0:
            l[0]=0
        DataRepository.add_meting(3,3,l[0],'weging toegevoegd')
        write = str(l[0])
        display.lcd_clear()
        display.print(write)

        socketio.emit('B2F_weging_gedaan', {'gewicht':f'{l[0]} gram'})

# def test3(userID):
#     data = DataRepository.get_history_by_goal(userID)
#     # print(data)
#     l = []
#     dates=[]
#     for i in data:
#         if i['serving']=='g':
#             qu=float(i['weight'])/float(i['portionServing'])
#             if i['datum'] not in dates:
#                 l.append({'Kcal':i['Kcal']*qu,'datum':i['datum']})
#                 dates.append(i['datum'])
#             else:
#                 place = dates.index(i['datum'])
#                 l[place]['Kcal']+=i['Kcal']*qu
#         else: 
#             if i['datum']  not in dates:
#                 l.append({'Kcal':i['Kcal'],'datum':i['datum']})
#                 dates.append(i['datum'])
#             else:
#                 place = datget_history_by_goales.index(i['datum'])
#                 l[place]['Kcal'] += i['Kcal']

    # print(l)

if __name__ == '__main__':
    try:
        ips = str(check_output(['ifconfig', 'wlan0']))
        startpos = ips.find("inet")+4
        ips = ips[startpos:].split(" ")
        display.print(ips[1])
        print("**** Starting APP ****")
        # DataRepository.add_food_to_meal(1,1,200)
        # print(test3(1))
        # DataRepository.get_goal_by_user(1)
        # print(DataRepository.get_food_by_barcode(x))
        # print(DataRepository.get_kleur(1))
        # DataRepository.get_goal_by_user(1)
        # huidig = DataRepository.get_goal_by_user(1)
        # print(huidig)
        start_thread()
        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt:
        print('KeyboardInterrupt exception is caught')
    finally:
        print("done")
        GPIO.cleanup()
