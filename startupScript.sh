#!/bin/sh
cd /
cd home/pi/Desktop/Pi-Zero-Fingerprint-Scanner
while [ 1 ]
do
        sudo python3 main.py
        sleep 10
done
cd /
