"""
This is the service that runs on the hotwater heater pi. It listens 
for the hotwater/power topic for these   messages: 

hotwater/power on     - the GPIO pin hat is controling the SSR of the hotwater heater is turned on
hotwater/power off    - the GPIO pin hat is controling the SSR of the hotwater heater is turned off 
hotwater/status       - the current state of the hotwater SCR is returned 
""" 

import paho.mqtt.client as mqtt 
import RPi.GPIO as GPIO 
import time

broker_address="192.168.2.48" 
power_pin = 26 #last pin on the header

cmd_topic = "hotwater/power"
sta_topic  = "hotwater/status"
on_msg    = "on"
off_msg   = "off"
exit_msg   = "exit"
clientid = "hw_device"
#clientid = "hw_controller"

Connected = False 

def on_message_1(client, userdata, message):
    print("\nmessage received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

def on_message(client, userdata, msg):
    print ("Topic: "+ msg.topic+"\nMessage: "+str(msg.payload.decode("utf-8")))
    if on_msg in msg.payload:
        print("Power on!")
        GPIO.output(power_pin, True)
    elif off_msg in msg.payload:
        print("Power Off!")
        GPIO.output(power_pin, False)
    elif exit_msg in msg.payload:
        print("Shutin down !")
        GPIO.cleanup()
    else:
        print("Unknown cmd")


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
        print("Connection failed")

def on_publish(client, userdata, mid):
    print ("on_publish mid: ",mid)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")



#----- MAIN ----- 

# Setup the GPIO pins before the callbacks , Board numbering  
GPIO.setmode(GPIO.BOARD) 
GPIO.setwarnings(False)
GPIO.setup(power_pin, GPIO.OUT) 

# Get the current state of the pin  
power_state = GPIO.input(power_pin)

print("creating new instance")
client = mqtt.Client(clientid) 

# when we get a message call this 
client.on_message=on_message

# handle logging 
client.onlog=on_log

client.on_subscribe=on_subscribe
client.on_connect=on_connect  

print("Starting connecting to broker")
client.connect(broker_address) 

# start the client loop to wait for incomming messages 
client.loop_start() 

# wait for the connection to be acked
while Connected != True: 
    time.sleep(0.1)

client.on_disconnect = on_disconnect
client.on_publish = on_publish

# set the value status  topic

print("Starting subscription cmd_topic",cmd_topic)
client.subscribe(cmd_topic)
print("Starting subscription sta_topic",sta_topic)
client.subscribe(sta_topic)

print("Publishing message to topic",cmd_topic)
client.publish(cmd_topic,on_msg)

time.sleep(2) # wait

print("Publishing message to topic",cmd_topic)
client.publish(cmd_topic,off_msg)

print("Publishing message to topic",cmd_topic)
client.publish(cmd_topic,exit_msg)

time.sleep(4) # wait
client.loop_stop() #stop the loop


