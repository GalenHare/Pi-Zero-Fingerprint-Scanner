import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time

red = 31
green = 33
blue = 35

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(red, GPIO.OUT) # Set pin 10 to be an input pin and set 
GPIO.setup(green, GPIO.OUT) # Set pin 10 to be an input pin and set 
GPIO.setup(blue, GPIO.OUT) # Set pin 10 to be an input pin and set 

while True:
	GPIO.output(red,1)
	print("1")
	time.sleep(3)
	GPIO.output(red,0)
	GPIO.output(green,1)
	print("2")
	time.sleep(3)
	GPIO.output(green,0)
	GPIO.output(blue,1)
	print("3")
	time.sleep(3)
	GPIO.output(blue,0)

