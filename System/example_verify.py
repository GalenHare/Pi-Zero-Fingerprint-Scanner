"""PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""
import requests
import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint


## Search for a finger
##

## Tries to initialize the sensor
try:
    f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

while(true):
    try:
        ID = input("Please enter ID of student")
        url = 'http://172.16.190.254:5000/api/fingerprint/' + str(ID)
        r = requests.get(url)
        if(r.status_code == 200)
        print(r.text)
        response = r.json
        print('Waiting for finger...')  

        ## Wait that finger is read
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)
        print("Input finger")
        scannedFinger = f.downloadCharacteristics(0x01)
        characteristics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
        print(scannedFinger)
        result,score = findFinger(response)
        if (result != 0):
            print("Finger found!")
            print(result)
            print("With an accuracy score: "+ str(score))
except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)


def findFinger(response):
    for x in response:
        temp = x["fingerprint"].split(", ")
        temp[0] = temp[0].split("[")[1]
        temp[temp.length-1] = temp[temp.length-1].split("]")[0]
        results = list(map(int, results))
        f.uploadCharacteristics(0x02,results)
        score = f.compareCharacteristics()
        if(score > 0):
            return x,score
    return 0 