"""
This is the controler that tells the HW driver what to do. 
the topic message that it publishes to are: 

hotwater/power on     - tells the HW driver to turn on the hotwater heater and returns the state  
hotwater/power off    - tells the HW driver to turn off the hotwater heater and returns the state  
hotwater/power get    - the current state of the hotwater SCR is returned with out changing it  

Typically this module is called to first getthe state and then if needed tset it to the desired state

python hw_ctrl.py --get <--debug>
python hw_ctrl.py --on
python hw_ctrl.py --off

The on message is published to the power topic and then the status topis is subscribed to 
to get the result of the command 
 
""" 

import paho.mqtt.client as mqtt 
import RPi.GPIO as GPIO 
import getopt
import sys 
import time

broker_address="192.168.2.48" 
#broker_address="192.168.2.10" 
power_pin = 37 #last pin on the header
MAXTIMEOUT = 30
DEBUG = 0 

cmd_topic = "hotwater/power"
sta_topic  = "hotwater/status"
on_msg    = "on"
off_msg   = "off"
exit_msg   = "exit"
get_msg = "get"
#clientid = "hw_device"
clientid = "hw_controller"

Connected = False
Gotstatus = -1 

def on_message_1(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

def on_message(client, userdata, msg):
    global Gotstatus 
    global DEBUG 

    if DEBUG: print ("Topic: "+ msg.topic+"\nMessage: "+str(msg.payload.decode("utf-8")))

    #  status message re sponce
    if sta_topic in msg.topic:
        if on_msg in msg.payload:
            Gotstatus = 1
        elif off_msg in msg.payload:
            Gotstatus = 0
        else:
            if DEBUG: print("Unknown status",msg.payload)


def on_log(client, userdata, level, buf):
    print("logging: ",buf)

def on_subscribe(client, userdata, mid, granted_qos):
    global DEBUG
    if DEBUG: print("Subscription acknowledged ")

def on_connect(client, userdata, flags, rc):
    global Connected                #Use global variable
    global DEBUG

    if rc == 0:
        if DEBUG: print("Connected to broker",broker_address)
        Connected = True                #Signal connection 
    else:
        print("Connection to broker failed")

def on_publish(client, userdata, mid):
    global DEBUG 
    if DEBUG: print ("on_publish mid: ",mid)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
    client.loop_stop() #stop the loop


def print_usage():
    print(
        "n.py [-n] [-f ] [-g] [-d]")



#----- MAIN -----
def main(argv):
    cmd = None
    verbose = False
    client_id = None
    dvr_id = "hw_device"
    ctl_id = "hw_controller"
    global DEBUG 

    try:
        opts, args = getopt.getopt(argv, "nfgd", ["on","off","get","debug"])
    except getopt.GetoptError as s:
        print_usage()
        sys.exit(4)

    client_id=ctl_id

    for opt, arg in opts:
        if opt in ("-n", "--on"):
            cmd = on_msg
        elif opt in ("-f", "--off"):
            cmd = off_msg
        elif opt in ("-g", "--get"):
            cmd = get_msg
        elif opt in ("-d", "--debug"):
            DEBUG = 1 


    if cmd == None:
        print("You must provide  cmd in controller mode.\n")
        print_usage()
        sys.exit(5)

    if DEBUG: print("creating new controller instance")
    client = mqtt.Client(client_id) 

    # couple call backs to handle
    client.on_message=on_message
    # client.on_log=on_log
    client.on_subscribe=on_subscribe
    client.on_connect=on_connect  
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    if DEBUG: print("Starting connecting to broker")
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
        sys.exit(6) 

    # clear any old messages and subscribe to the status topic
    if DEBUG:  print("Starting subscription sta_topic",sta_topic)
    client.subscribe(sta_topic,1)

    # send the message  
    if DEBUG: print("Publishing ",cmd," to topic",cmd_topic)
    client.publish(cmd_topic,cmd)

    # wait for the responce 
    timeout = 0
    while Gotstatus < 0 and timeout < MAXTIMEOUT: 
        time.sleep(0.1)
        timeout += 1 
        if DEBUG: print ("waiting for status ",Gotstatus, timeout ) 
    
    client.unsubscribe(sta_topic)
    client.loop_stop()
    client.disconnect()
    print Gotstatus 


if __name__ == "__main__":
    main(sys.argv[1:])


