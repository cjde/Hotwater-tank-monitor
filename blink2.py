import RPi.GPIO as GPIO ## Import GPIO Library
import time ## Import 'time' library.  Allows us to use 'sleep'
PIN =  11
GPIO.setmode(GPIO.BOARD) ## Use BOARD pin numbering
GPIO.setup(PIN, GPIO.OUT)

## Define function named Blink()
def Blink(numTimes, on, off):
    for i in range(0,numTimes):
#        print "Iteration " + str(i+1)
        GPIO.output(PIN,True)
        time.sleep(on)
        GPIO.output(PIN, False)
        time.sleep(off)
#    print "Done"
    GPIO.cleanup()

## Prompt user for input
#cycle = raw_input("Enter the length of the blink cycle: ")
cycle = 59

#on = raw_input("Enter tmout of time it should be on, in seconds: ")
on = 0.01

#off = raw_input("Enter tmout of time it should be off, in seconds: ")
off = 0.9

# this script runs in cron every minute and need to finish in that time or there will be several running.
iterations = cycle / ( on + off )

## Start Blink() function. Convert user input from strings to numeric data types and pass to Blink() as parameters
Blink(int(iterations),float(on),float(off) )


