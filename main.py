import requests
import json
import hashlib
import time
import datetime
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
from pyfingerprint.pyfingerprint import PyFingerprint
from lcd import lcddriver
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import keyboard
import pymongo


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["offlineDB"]

offlineRecords = db["offlineRecords"]



upButton = 36
downButton = 38
selectButton = 40
red = 31
green = 33
blue = 35

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(upButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 10 to be an input pin and set 
GPIO.setup(downButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 10 to be an input pin and set 
GPIO.setup(selectButton, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 10 to be an input pin and set 

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(red, GPIO.OUT) # Set pin 10 to be an input pin and set 
GPIO.setup(green, GPIO.OUT) # Set pin 10 to be an input pin and set 
GPIO.setup(blue, GPIO.OUT) # Set pin 10 to be an input pin and set 

display= lcddriver.lcd()
url = "http://192.168.1.140:5000/"
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
password = "value1"
scannerID = 1
endDay = -1
endHour = -1
endMinute = -1
courseCode = 0
startMinute = -1
status = 0
ID = ""
entered = 0

## Main program
def main():
    initializeSensor()
    checkConnection()
    while(True):
        ###try:
        checkConnection2()
        print(status)
        updateCourse()
        print("Welcome to the the Registration Authentication Unit")
        selection = None
        display.lcd_clear()
        display.lcd_display_string("Please select an", 1)
        display.lcd_display_string("option", 2)
        time.sleep(3)
        display.lcd_clear()
        option = 0
        while(selection != "j"):
            if(status==0):
                flushDB()
            display.lcd_display_string("1.Enroll", 1)
            display.lcd_display_string("2.Mark", 2)
            print("Please select an option from below")
            print("\t1:Enroll a fingerprint\n\t2:Mark Attendance")
            checkConnection2()
            ##TODO: Ensure admin user before enrolling a fingerprint
            selection = buttonInput()
            if(selection == "w" or selection == "s"):
                option+=1
                display.lcd_clear()
                if(option%2==0):
                    display.lcd_display_string("1.Enroll", 1)
                    display.lcd_display_string("2.Mark<<<<<", 2)
                else:
                    display.lcd_display_string("1.Enroll<<<<<", 1)
                    display.lcd_display_string("2.Mark", 2)
            elif(selection!="j"):
                print("Invalid selection please try again")
                display.lcd_clear(  )
                display.lcd_display_string("Invalid Selction", 1)
                time.sleep(2)
        if(option %2 == 1):
            enrollFingerprint()
        elif(option %2 == 0):
            markAttendance()

# AES 256 encryption/decryption using pycrypto library 
def encrypt(raw, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))
 
 
def decrypt(enc, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return bytes.decode(unpad(cipher.decrypt(enc[16:])))
 
def key_press(key):
    global ID,entered
    print(key.name)
    if(key.name!="enter"):
        ID = ID + key.name
        print(ID)
    else:    
        entered=1

keyboard.on_press(key_press)

def initializeSensor():
    ## Tries to initialize the sensor
    state = None
    for x in range(2):
        ledControl("green")
        display.lcd_display_string(" Welcome to the ", 1)
        display.lcd_display_string("     R.A.U.  ", 2)
        time.sleep(2)
        ledControl("off")
        display.lcd_clear() 
        time.sleep(1)
    display.lcd_clear()
    while(state == None):
        try:
            display.lcd_display_string("Initializing...", 1)
            time.sleep(1)
            print("Initializing fingerprint sensor...")
            global f
            f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000) 
            if ( f.verifyPassword() == False ):
                ledControl("red")
                raise ValueError('The given fingerprint sensor password is wrong!')
            print("Fingerprint sensor successfully initialized")
            state = 1
            display.lcd_display_string("....Success!....", 1)
            ledControl("green")
            time.sleep(2)
            ledControl("off")
            display.lcd_clear()
        except Exception as e:
            display.lcd_display_string("Failed retrying", 1)
            ledControl("red")
            time.sleep(3)
            display.lcd_clear()
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
def markAttendance():
    global ID,entered
    display.lcd_clear()
    display.lcd_display_string("Scan Barcode...",1)
    while(entered == 0):
        time.sleep(1)
    entered = 0
    display.lcd_clear()
    display.lcd_display_string("ID: "+ID,1)
    ledControl("green")
    time.sleep(2)
    ledControl("off")
    if status == 0:
        temp = url +'api/fingerprint/id/' + str(ID)
        r = requests.get(temp)
        r.raise_for_status()
        response = r.json()
        print(response)
        if(response == []):
            print("Empty JSON response")
            display.lcd_clear()
            display.lcd_display_string("No student found!",1)
            ledControl("red")
            time.sleep(3)
            ledControl("off")
            ID = ""
            return
    print('Waiting for finger...')  
    display.lcd_clear()
    display.lcd_display_string("Place Finger...",1)
    print('Waiting for finger...')
    ledControl("blue")
    while(f.readImage() == False):
        pass
    f.convertImage(0x01)
    ledControl("green")
    print('Remove finger...')
    display.lcd_clear()
    display.lcd_display_string("Remove Finger...",1)
    time.sleep(2)
    ledControl("blue")
    print('Place same finger...')
    display.lcd_clear()
    display.lcd_display_string("Place same",1)
    display.lcd_display_string("finger...",2)
    while(f.readImage() == False):
        pass
    f.convertImage(0x02)
    ledControl("green")
    ##Creates a template
    f.createTemplate()
    scannedFinger = f.downloadCharacteristics(0x01)
    print("SCANNED FINGER")
    print(scannedFinger)
    print("====================================================")
    ledControl("off")
    if status == 0:
        for x in response:
            temp = decrypt(x["fingerprint"].encode(),password).split(", ")
            temp[0] = temp[0].split("[")[1]
            temp[len(temp)-1] = temp[len(temp)-1].split("]")[0]
            results = list(map(int, temp))
            print (results) 
            f.uploadCharacteristics(0x02,results)
            score = f.compareCharacteristics()
            if(score > 0):
                break 
        if (score != 0):
            display.lcd_clear()
            display.lcd_display_string("Fingerprint",1)
            display.lcd_display_string("verified",2)
            ledControl("green")
            time.sleep(3)
            ledControl("off")
            print(results)
            print("Finger found!")
            print("With an accuracy score: "+ str(score))
            attendanceRequest(ID)
        else:
            display.lcd_clear()
            display.lcd_display_string("Fingerprint",1)
            display.lcd_display_string("not verified!",2)
            ledControl("red")
            time.sleep(2)
            ledControl("off")
            print("Finger not found")
    else:
        tempRecord = {"option":"2","ID":str(ID),"fingerprint":str(scannedFinger),"current":timeParser('JSFormat'),"checked":0}
        offlineRecords.insert(tempRecord)
    ID = ""


def enrollFingerprint():
    global ID,entered
    ## Tries to enroll a new finger
    display.lcd_clear()
    display.lcd_display_string("Scan Barcode...",1)
    print('Please enter ID of student...')
    ledControl("blue")
    while(entered == 0):
        time.sleep(1)
    entered = 0
    display.lcd_clear()
    display.lcd_display_string("ID: "+ID,1)
    ledControl("green")
    time.sleep(2)
    ledControl("off")
    display.lcd_clear()
    display.lcd_display_string("Place Finger...",1)
    print('Waiting for finger...')
    ledControl("blue")
    #Wait that finger is read
    while(f.readImage() == False):
        pass
    ## Converts read image to characteristics and stored it in charbuffer 1
    ledControl("green")
    f.convertImage(0x01)
    print('Remove finger...')
    display.lcd_clear()
    display.lcd_display_string("Remove Finger...",1)
    time.sleep(2)
    ledControl("blue")
    print('Place same finger...')
    display.lcd_clear()
    display.lcd_display_string("Place same",1)
    display.lcd_display_string("finger...",2)
    #Wait until that finger is read again
    while(f.readImage() == False):
        pass
    ##Converts read image to characterisitics and stored it in charbuffer 2 
    ledControl("green")  
    f.convertImage(0x02)
    ## Compares the charbuffers
    if( f.compareCharacteristics() == 0):
        display.lcd_clear()
        display.lcd_display_string("Fingers do not",1)
        display.lcd_display_string("match!",2)
        ledControl("red")
        time.sleep(3)
        ledControl("off")
        display.lcd_clear()
        ID = ""
        return
    display.lcd_clear()
    display.lcd_display_string("Enrolling....",1)
    ledControl("blue")
    ##Creates a template
    f.createTemplate()
    ##Saves template at new position number
    characteristics = str(f.downloadCharacteristics(0x01))
    print(characteristics)
    fingerprint = encrypt(characteristics,password)
    print(fingerprint)
    payload = {'studentID':str(ID),'fingerprint':fingerprint}
    if status == 0:
        print("Online mode")
        r = requests.post(url+'api/fingerprint',json = payload)
        r.raise_for_status()
        print(r.text)
        print("Success")
        display.lcd_clear()
        display.lcd_display_string("Enrollment",1)
        display.lcd_display_string("Succesful!",2)
        ledControl("green")
        time.sleep(3)
        ledControl("off")
        display.lcd_clear()
    else:
        print("Offline mode")
        tempRecord = {"option":"1","ID":str(ID),"fingerprint":str(fingerprint),"checked":0}
        offlineRecords.insert(tempRecord)
    ID = ""



def attendanceRequest(id):
    payload = {'studentID':id,"date":timeParser('JSFormatZ'),'courseCode':courseCode,"scannerID":str(scannerID)}
    print(payload)
    r = requests.post(url+'api/attendance',json = payload)
    r.raise_for_status()
    print(r.text)



def updateCourse():
    global courseCode,endDay,startMinute,endMinute 
    if status == 0:
        print("Updating Course")
        currentDateTime = datetime.datetime.now()
        currentMinute = timeParser("currentTimeMins")
        print(currentMinute)
        if(currentMinute >= endMinute or endDay != int(currentDateTime.strftime("%w"))):
            payload = {"_id":scannerID,"currentDate":timeParser("JSFormat")}
            print(payload)
            r = requests.get(url+'api/scanner/course',params = payload)
            r.raise_for_status()
            response = r.json()
            print(response)
            if(response == []):
                display.lcd_clear()
                display.lcd_display_string("No Course found",1)
                display.lcd_display_string("for this time",2)
                time.sleep(3)
                display.lcd_clear()
                courseCode,endDay,startMinute,endMinute = -1,-1,-1,-1
            else:
                display.lcd_clear()
                display.lcd_display_string("Current Course",1)
                tempString = str(response[0]['courseCode'])
                display.lcd_display_string(tempString,2)
                time.sleep(3)
                display.lcd_clear()
                courseCode,endDay,startMinute,endMinute = response[0]['courseCode'],response[0]['day'],response[0]['startMinute'],response[0]['endMinute']

    
    

def timeParser(option):
    currentDateTime = datetime.datetime.now()
    if(option == 'currentTimeMins'):
        return currentDateTime.hour * 60 + currentDateTime.minute
    elif(option == 'currentDay'):
        return int(currentDateTime.strftime("%w"))
    elif(option == 'JSFormat'):
        return currentDateTime.strftime("%Y-%m-%dT%X")
    elif(option == 'JSFormatZ'):
        return currentDateTime.strftime("%Y-%m-%dT%X")+"Z"
        
def buttonInput():
    while True:
        if(GPIO.input(upButton) == False):
            return "w"
        if(GPIO.input(downButton) == False):
            return "s"
        if(GPIO.input(selectButton) == False):
            return "j"

def ledControl(colour):
    if(colour=="red"):
        GPIO.output(red,1)
        GPIO.output(green,0)
        GPIO.output(blue,0)
    if(colour=="green"):
        GPIO.output(green,1)
        GPIO.output(red,0)
        GPIO.output(blue,0)
    if(colour=="blue"):
        GPIO.output(blue,1)
        GPIO.output(green,0)
        GPIO.output(red,0)
    if(colour=="off"):
        GPIO.output(blue,0)
        GPIO.output(green,0)
        GPIO.output(red,0)
def checkConnection():
    global status
    try:
        display.lcd_display_string("Contacting",1)
        display.lcd_display_string("server...",2)
        time.sleep(1)
        r = requests.get(url,timeout=10)
        r.raise_for_status()
        display.lcd_clear()
        display.lcd_display_string("Connection",1)
        display.lcd_display_string("successful!",2)
        ledControl("green")
        time.sleep(3)
        ledControl("off")
        display.lcd_clear()
    except Exception as e:
        print("Connection server failed!")
        ledControl("red")
        display.lcd_display_string("Connection", 1)
        display.lcd_display_string("failed", 2)
        time.sleep(1)
        display.lcd_clear()
        display.lcd_display_string("Entering", 1)
        display.lcd_display_string("Offline mode", 2)
        time.sleep(3)
        display.lcd_clear()
        ledControl("off")
        status = 1
        print('Exception message: ' + str(e))

def checkConnection2():
    global status
    try:
        r = requests.get(url,timeout=2)
        r.raise_for_status()
        status = 0
    except Exception as e:
        status = 1
        print('Exception message: ' + str(e))

def flushDB():
    print("Flushing file")
    for i in offlineRecords.find({"checked":0}):
        print(i)
        if(i['option']=="1"):
            payload = {'studentID':str(i['ID']),'fingerprint':str(i['fingerprint'])}
            print(payload)
            r = requests.post(url+'api/fingerprint',json = payload)
            r.raise_for_status()
            print(r.text)
            print("Success")
        else:
            temp2 = i['fingerprint'].split(", ")
            temp2[0] = temp2[0].split("[")[1]
            temp2[len(temp2)-1] = temp2[len(temp2)-1].split("]")[0]
            result = list(map(int, temp2))
            print(result)
            f.uploadCharacteristics(0x01,result)
            temp = url +'api/fingerprint/id/' + str(i['ID'])
            r = requests.get(temp)
            r.raise_for_status()
            response = r.json()
            #print(response)
            if(response != []):
                for x in response:
                    temp = decrypt(x["fingerprint"].encode(),password).split(", ")
                    temp[0] = temp[0].split("[")[1]
                    temp[len(temp)-1] = temp[len(temp)-1].split("]")[0]
                    results = list(map(int, temp))
                    print (results) 
                    f.uploadCharacteristics(0x02,results)
                    score = f.compareCharacteristics()
                    print(score)
                    if(score > 0):
                        break 
                if (score != 0):
                    payload = {"_id":scannerID,"currentDate":str(i['current'])}
                    r = requests.get(url+'api/scanner/course',params = payload)
                    r.raise_for_status()
                    response = r.json()
                    print("Matched a finger")
                    if(response != []):
                        payload = {'studentID':id,"date":str(i['current']),'courseCode':response[0]['courseCode'],"scannerID":str(scannerID)}
                        print(payload)
                        r = requests.post(url+'api/attendance',json = payload)
                        r.raise_for_status()
                        print(r.text)
                        print("Success!")
        offlineRecords.update(i,{ "$set": { "checked": 1 } })

        

if __name__ == '__main__':
    main()
