import RPi.GPIO as GPIO
import time
from threading import Thread

counter = 0
perhour = 0

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN)
    if GPIO.input(17) == 1:
        pass
    else:
        global counter
        counter = counter + 0.001
        return counter
    GPIO.cleanup() 
    time.sleep(0.1)
    main()

def everymin(perhour):
    perhour = 0
    global counter
    perhour = counter * 60 # get the counter and get what it would be per hour
    counter = 0 # reset the variable
    print("m sv/hr: " + str(perhour))
    time.sleep(60) # delay 60 seconds
    everymin(perhour)


Thread(target=main,).start()
Thread(target=everymin, args=(perhour,)).start()
