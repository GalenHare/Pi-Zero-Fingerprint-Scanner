#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests 
from pyfingerprint.pyfingerprint import PyFingerprint

## Enrolls a new finger
##

##Tries to initialize the sensor 
try: 
	f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000)

	if ( f.verifyPassword() == False):
                raise ValueError('The given fingerprint sensor password is wrong')

except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

## Gets some sensor information
print('Currently used templates: ' + str(f.getTemplateCount()) + '/' + str(f.getStorageCapacity()))

## Tries to enroll a new finger
try:
        print('Waiting for finger...')

        #Wait that finger is read
        while(f.readImage() == False):
                pass

        ## Converts read image to characteristics and stored it in charbuffer 1
        f.convertImage(0x01)

        #Checks if finger is already enrolled
        result = f.searchTemplate()
        positionNumber = result[0]

        if (positionNumber >= 0):
                print('Template already exists at postition #' + str(positionNumber))
                exit(0)


        print('Remove finger...')
        time.sleep(2)

        print('Place same finger...')

        #Wait until that finger is read again
        while(f.readImage() == False):
                pass

        ##Converts read image to characterisitics and stored it in charbuffer 2
        
        f.convertImage(0x02)

        ## Compares the charbuffers
        if( f.compareCharacteristics() == 0):
                raise Exception('Fingers do not match')

        ##Creates a template
        f.createTemplate()

        ##Saves template at new position number
        positionNumber = f.storeTemplate()
        print('Finger enrolled successfully')
        print('New template position #' + str(positionNumber))

        r = requests.get('http://192.168.1.192:3000/api/attendance')
        print(r.text)

except Exception as e:
        print('Operation failed')
        print('Exception message: ' + str(e))
        exit(1)
        
