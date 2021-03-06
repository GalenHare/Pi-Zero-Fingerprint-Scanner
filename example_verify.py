"""PyFingerprint cvx
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

while(True):
    try:
        ID = input("Please enter ID of student")
        url = 'http://192.168.0.12:5000/api/fingerprint/' + str(ID)
        r = requests.get(url)
        r.raise_for_status()
        response = r.json()
        #print(response)
        print('Waiting for finger...')  

        ## Wait that finger is read
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)
        print("Input finger")
        scannedFinger = f.downloadCharacteristics(0x01)
        characteristics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
        print("SCANNED FINGER")
        print(scannedFinger)
        print("====================================================")
        for x in response:
          #  print(x)
            temp = x["fingerprint"].split(", ")
            temp[0] = temp[0].split("[")[1]
            temp[len(temp)-1] = temp[len(temp)-1].split("]")[0]
            results = list(map(int, temp))
            print (results) 
            f.uploadCharacteristics(0x02,results)
            score = f.compareCharacteristics()
            if(score > 0):
                break 
        if (score != 0):
            print("Finger found!")
            print(results)
            print("With an accuracy score: "+ str(score))
        else:
            print("Finger not found")
    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)



