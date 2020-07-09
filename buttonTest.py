from lcd import lcddriver
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 10 to be an input pin and set 
GPIO.setup(38, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 10 to be an input pin and set 
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 10 to be an input pin and set 

display= lcddriver.lcd()

while True:
    if GPIO.input(36) == False:
        display.lcd_clear()
        display.lcd_display_string("Button 1", 1)
    if GPIO.input(38) == False:
        display.lcd_clear()
        display.lcd_display_string("Button 2", 1)
    if GPIO.input(40) == False:
        display.lcd_clear()
        display.lcd_display_string("Button 3", 1)

