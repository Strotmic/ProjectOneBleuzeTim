import serial
# import repositories.adafruit_fingerprintClass as adafruit_fingerprint
import adafruit_fingerprint
from repositories.DataRepository import DataRepository
import json

uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

array = []

##################################################


def sensor_reset():
    """Reset sensor"""
    print("Resetting sensor...")
    if finger.soft_reset() != adafruit_fingerprint.OK:
        print("Unable to reset sensor!")
    print("Sensor is reset.")


# pylint: disable=too-many-branches
def fingerprint_check_file():
    """Compares a new fingerprint template to an existing template stored in a file
    This is useful when templates are stored centrally (i.e. in a database)"""
    print("Waiting for finger print...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False

    print("Loading file template...", end="")
    data = DataRepository.get_all_fingerprints()
    # print(data)
    for x in data:
        data = (x['fingerScan'])
        print(data)
        print('-'*40)
        try:
            data = json.loads(data)

            finger.send_fpdata((data), "char", 2)

            i = finger.compare_templates()
            if i == adafruit_fingerprint.OK:
                print("Fingerprint match template in file.")
                print(x['userID'])
                return True
            if i == adafruit_fingerprint.NOMATCH:
                print("Templates do not match!")

            else:
                print("Other error!")
        except:
            return False
    return False


# pylint: disable=too-many-statements
def enroll_save_to_file():
    """Take a 2 finger images and template it, then store it in a file"""
    number = input('geef het id: >>')
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="")
        else:
            print("Place same finger again...", end="")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
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

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Downloading template...")
    data = finger.get_fpdata("char", 1)
    DataRepository.add_fingerprint(number, str(data))
    print("Template is saved in template0.dat file.")

    return True


while True:
    x = fingerprint_check_file()
    if x:
        print('oke')
    else: print('niet oke')
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates: ", finger.templates)
    if finger.count_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Number of templates found: ", finger.template_count)
    if finger.set_sysparam(6, 2) != adafruit_fingerprint.OK:
        raise RuntimeError("Unable to set package size to 128!")
    if finger.read_sysparam() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to get system parameters")
    print("Package size (x128):", finger.data_packet_size)
    print("Size of template library: ", finger.library_size)
    print("e) enroll print and save to file")
    print("c) compare print to file")
    print("r) soft reset")
    print("x) quit")
    print("----------------")
    c = input("> ")

    if c in ("x", "q"):
        print("Exiting fingerprint example program")
        # turn off LED
        raise SystemExit
    if c == "e":
        enroll_save_to_file()
    elif c == "c":
        fingerprint_check_file()
    elif c == "r":
        sensor_reset()
    else:
        print("Invalid choice: Try again")
