#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyFingerprint
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

## Gets some sensor information
print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

## Tries to search the finger and calculate hash
try:
    #ID = input("Please enter your student id...")
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
    ## Searchs template
    result = f.searchTemplate()
    positionNumber = result[0]
    accuracyScore = result[1]

    if ( positionNumber == -1 ):
        print('No match found!')
        exit(0)
    else:
        print('Found template at position #' + str(positionNumber))
        print('The accuracy score is: ' + str(accuracyScore))

    ## OPTIONAL stuff
    ##

    ## Loads the found template to charbuffer 1
    f.loadTemplate(positionNumber, 0x01)

    ## Downloads the characteristics of template loaded in charbuffer 1
    print(len(f.downloadCharacteristics(0x01)))
    storedFinger = f.downloadCharacteristics(0x01)
    characteristics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
    print(characteristics)
    #print("Searching..")
    ## Hashes characteristics of template
    print('SHA-2 hash of template: ' + hashlib.sha256(characteristics).hexdigest())
    sum = 0
    for x in range(0,len(scannedFinger)):
        if(scannedFinger[x]> storedFinger[x]-1 and scannedFinger[x]<storedFinger[x]+1 and scannedFinger[x]!= 0):
            sum = sum + 1
    print("Calculated accuracy score: " + str(sum))
    
        
    #payload = {'studentID':str(ID),'fingerprint':characteristics}
    ##r = requests.post('http://172.16.190.254:5000/api/fingerprint/search',json = payload)
    ##print(r.text)
except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
