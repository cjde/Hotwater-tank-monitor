"""
This is the service that runs on the hotwater heater pi. It listens 
continously for the hotwater/power topic for these   messages: 

hotwater/power on     - the GPIO pin hat is controling the SSR of the hotwater heater is turned on
hotwater/power off    - the GPIO pin hat is controling the SSR of the hotwater heater is turned off 
hotwater/status       - the current state of the hotwater SCR is returned 
""" 

import paho.mqtt.client as mqtt 
import RPi.GPIO as GPIO 
import time
import getopt
import sys

broker_address="192.168.2.48" 
power_pin = 26 #last pin on the header
MAXTIMEOUT = 60 

cmd_topic  = "hotwater/power"
sta_topic  = "hotwater/status"
on_msg     = "on"
off_msg    = "off"
exit_msg   = "exit"
get_msg    = "get"
unk_msg    = "unknown"
clientid  = "hw_device"
#clientid = "hw_controller"

Connected = False 
Gotstatus = "" 

def on_message_1(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

def on_message(client, userdata, msg):
    print ("Topic: "+ msg.topic+"\nMessage: "+str(msg.payload.decode("utf-8")))

    # Do we have command topic ? 
    if cmd_topic in msg.topic: 
        if on_msg in msg.payload:
            print("Power on!")
            GPIO.output(power_pin, True)
            Gotstatus = on_msg 
        elif off_msg in msg.payload:
            print("Power Off!")
            GPIO.output(power_pin, False)
            Gotstatus = off_msg 
        elif get_msg in msg.payload:
            print("Gettin status !")
            if GPIO.input(power_pin) == 1: 
                Gotstatus = on_msg 
            else:
                Gotstatus = off_msg 
        elif exit_msg in msg.payload:
            print("Shutin down !")
            GPIO.cleanup()
            Gotstatus = exit_msg 
            client.loop_stop() 
        else:
            print("Unknown Command",msg.payload)
            Gotstatus = unk_msg  

    # send the the status message back to the caller on the status topic 
    print("Publishing ",Gotstatus," to topic",sta_topic)
    client.publish(sta_topic,Gotstatus)

def on_log(client, userdata, level, buf):
    print("logging: ",level,buf)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscription acknowledged ")

def on_connect(client, userdata, flags, rc):
    global Connected                #Use global variable

    if rc == 0:
        print("Connected to broker")
        Connected = True                #Signal connection 
    else:
        print("Connection to broker failed")

def on_publish(client, userdata, mid):
    print ("on_publish mid: ",mid)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
    client.loop_stop() #stop the loop

def print_usage():
    print(
        "n.py [-g] ")



#----- MAIN ----- 
def main(argv):
    cmd = None
    verbose = False
    client_id = None
    dvr_id = "hw_device"
    ctl_id = "hw_controller"

    try:
        opts, args = getopt.getopt(argv, "d", ["debug"])
    except getopt.GetoptError as s:
        print_usage()
        sys.exit(2)

    client_id=dvr_id

    for opt, arg in opts:
        if opt in ("-d", "--debug"):
            debug = 1 

    print("creating new controller instance")
    client = mqtt.Client(client_id)


    # Setup the GPIO pins before the callbacks , Board numbering  
    GPIO.setmode(GPIO.BOARD) 
    GPIO.setwarnings(False)
    GPIO.setup(power_pin, GPIO.OUT) 



    print("creating new controller instance")
    client = mqtt.Client(client_id)

    # couple call backs to handle
    client.on_message=on_message
    client.on_log=on_log
    client.on_subscribe=on_subscribe
    client.on_connect=on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    print("Starting connecting to broker")
    client.connect(broker_address)

    # start the client loop to wait for incomming messages
    client.loop_start()

    # wait for the connection to the broker be acked
    timeout = 0
    while Connected != True and timeout < MAXTIMEOUT:
        timeout += 1
        time.sleep(0.1)

    if timeout == MAXTIMEOUT :
        print (" timed out waiting for connection to broker" )
        sys.exit(2)

    # subscribe to the command topic 
    print("Starting subscription cmd_topic",cmd_topic)
    client.subscribe(cmd_topic)

    # start the client loop to wait for incomming messages 
    client.loop_forever() 


if __name__ == "__main__":
    main(sys.argv[1:])

