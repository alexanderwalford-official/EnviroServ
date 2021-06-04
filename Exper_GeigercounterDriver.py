# driver for the KKmoon Nuclear Radiation Detector
# Alexander Walford 2021


import RPi.GPIO as GPIO
import time
from threading import Thread

counter = 0
perhour = 0

def main():
    # GPIO settings
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN)
    if GPIO.input(17) == 1:
        pass
        # High pulse, ignore this as we are only looking for breaks in the pulses.
    else:
        # Low pulse
        global counter
        counter = counter + 0.001
        return counter
    GPIO.cleanup() 
    time.sleep(0.1)
    Thread(target=main,).start()

def everymin(perhour):
    global counter # reference to the global variable
    perhour = counter * 60 # get the counter and get what it would be per hour
    counter = 0 # reset the variable
    print("m sv/hr: " + str(perhour))
    time.sleep(60) # delay 60 seconds
    Thread(target=everymin, args=(perhour,)).start()

# Threading that allows both functions to operate simultaneously
Thread(target=main,).start()
Thread(target=everymin, args=(perhour,)).start()