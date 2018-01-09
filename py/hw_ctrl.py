"""
This is the controler that tells the HW driver what to do. 
the topic that it publishes to are: 

hotwater/power on     - tells the HW driver to turn on the hotwater heater and returns the state  
hotwater/power off    - tells the HW driver to turn off the hotwater heater and returns the state  
hotwater/power get    - the current state of the hotwater SCR is returned with out changing it  

Typically this module is called to first getthe state and then if needed tset it to the desired state

python hw_ctrl.py --get
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
power_pin = 26 #last pin on the header

cmd_topic = "hotwater/power"
sta_topic  = "hotwater/status"
on_msg    = "on"
off_msg   = "off"
exit_msg   = "exit"
get_msg = "get"
clientid = "hw_device"
#clientid = "hw_controller"

Connected = False
Gotstatus = -1 

def on_message_1(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

def on_message(client, userdata, msg):
    print ("Topic: "+ msg.topic+"\nMessage: "+str(msg.payload.decode("utf-8")))

    #  status message re sponce
    if sta_topic in msg.topic:
        if on_msg in msg.payload:
            Gotstatus = 1
        elif off_msg in msg.payload:
            Gotstatus = 0
        else:
            print("Unknown status",msg.payload)


def on_log(client, userdata, level, buf):
    print("logging: ",buf)

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

def print_usage():
    print(
        "n.py [-n] [-f ] [-g] ")



#----- MAIN -----
def main(argv):
    client_id = None
    cmd = None
    verbose = False
    client_id = None
    dvr_id = "hw_device"
    ctl_id = "hw_controller"

    try:
        opts, args = getopt.getopt(argv, "nfg", ["on","off","get"])
    except getopt.GetoptError as s:
        print_usage()
        sys.exit(2)

    client_id=ctl_id

    for opt, arg in opts:
        if opt in ("-n", "--on"):
            cmd = on_msg
        elif opt in ("-f", "--off"):
            cmd = off_msg
        elif opt in ("-g", "--get"):
            cmd = get_msg


    if cmd == None:
        print("You must provide  cmd in controller mode.\n")
        print_usage()
        sys.exit(2)

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
    while Connected != True: 
        time.sleep(0.1)

    # clear any old messages and subscribe to the status topic
    print("Starting subscription sta_topic",sta_topic)
    client.subscribe(sta_topic,1)

    # send the message  
    print("Publishing ",cmd," to topic",cmd_topic)
    client.publish(cmd_topic,cmd)

    # wait for the responce 
    timeout = 0
    while Gotstatus < 0 and timeout < 25: 
        time.sleep(0.1)
        timeout += 1 
        print ("waiting for status ") 
    
    client.unsubscribe(sta_topic)
    client.disconnect()
    print ( Gotstatus )


if __name__ == "__main__":
    main(sys.argv[1:])


