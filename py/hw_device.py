"""
This is the service that runs on the hotwater heater pi. It listens 
for the hotwater/power topic for these   messages: 

hotwater/power on     - the GPIO pin hat is controling the SSR of the hotwater heater is turned on
hotwater/power off     - the GPIO pin hat is controling the SSR of the hotwater heater is turned off 
hotwater/power status - the current state of the hotwater SCR is returned 
""" 

import paho.mqtt.client as mqtt 
import time

broker_address="192.168.2.48" 

topic     = "hotwater/power"
on_msg    = "on"
off_msg   = "off"
st_msg    = "status"

Connected = False 

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

def on_log(client, userdata, level, buf):
    print("log: ",buf)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscription acknowledged ")

def on_connect(client, userdata, flags, rc):
    global Connected                #Use global variable

    if rc == 0:
        print("Connected to broker")
        Connected = True                #Signal connection 
    else:
        print("Connection failed")



print("creating new instance")
client = mqtt.Client("P1") 

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

print("Starting subscription topic",topic)
client.subscribe(topic)

print("Publishing message to topic",topic)
client.publish(topic,on_msg)
time.sleep(4) # wait
client.loop_stop() #stop the loop


