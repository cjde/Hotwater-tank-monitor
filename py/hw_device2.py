"""
This is the service that runs on the hotwater heater pi. It listens
continously on the hotwater/power and publishes on the hotwater/statys
topic for these   messages:

hotwater/power ON     - the GPIO pin hat is controling the SSR of the hotwater heater is turned on
hotwater/power OFF    - the GPIO pin hat is controling the SSR of the hotwater heater is turned off
hotwater/status       - the current state of the hotwater SCR is returned
"""

import paho.mqtt.client as mqtt
import json
import re
import argparse
import RPi.GPIO as GPIO
import os


# message from MQTT ( in "byte" format )
PAYLOAD = ''
DEBUG = ""
CMDTOPIC    =  "hotwater-v2/power"
STATUSTOPIC = "hotwater-v2/status"
myhost = os.uname()[1]
CLIENTID    = "hw_devicev2" + "-" +  myhost
PORT = 1883
MAXTIMEOUT = 60
ON_MSG     = 'ON'
OFF_MSG    = 'OFF'
STATUS_MSG = 'GET'
DEVICESTATE  = "Unknown"
BADJSON = "-1"
MQTTbroker = "homeassistant.hm"
User = "mqttuser"
Password = "mqttpass"

#last pin on the header, FYI pin 39 is GND so use a 56 ohm resister with a test LED
power_pin = 37


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # valid JSON message format
    # [{"linenum": 0, "msg": "BTU: 17023","backlight":1}]

    global PAYLOAD,DEVICESTATE

    PAYLOAD = msg.payload

    if DEBUG:
        print("Got message topic: ", msg.topic + " Payload: " + str(PAYLOAD))

    # check if it is a off or on message from homeassistant. Light devices send just byte codws
    try:
        decoded = msg.payload.decode('UTF-8')

        if decoded == STATUS_MSG:
            if DEBUG: print("STATUS")
            if DEBUG: print("Publishing ", DEVICESTATE, " to topic", STATUSTOPIC)
            client.publish(STATUSTOPIC, DEVICESTATE)
        elif decoded == ON_MSG :
            if DEBUG: print("ON")
            try:
                GPIO.output(power_pin, True)
            except:
                print("Can't set GPIO on pin:", power_pin)
                GPIO.cleanup()
            DEVICESTATE = decoded
        elif decoded == OFF_MSG:
            if DEBUG: print("OFF")
            try:
                GPIO.output(power_pin, False)
            except:
                print("Can't set GPIO on pin:", power_pin)
                GPIO.cleanup()
            DEVICESTATE = decoded
        else:
            # check if it is valid JSON data
            print (" checking JSON")
            try:
                dic = json.loads(decoded)
            except ValueError as e:
                print ("Bad JSON message: ",str(PAYLOAD))
                client.publish(STATUSTOPIC, BADJSON)
                return False

            if DEBUG:
                print ("JSON payloads:",len(dic), dic )
            return True
    except:
        print ("Bad data in binary message: ",str(PAYLOAD))
        return False

def on_connect(client, userdata, flags, rc):
    '''
    Subscribes to the hotwater topic and prints the message
    The callback for when the client receives a CONNACK response from the server.

    Connection Return Codes
    0: Connection successful
    1: Connection refused – incorrect protocol version
    2: Connection refused – invalid client identifier
    3: Connection refused – server unavailable
    4: Connection refused – bad username or password
    5: Connection refused – not authorised
'''
    if  rc == 0 :
        print("Connected OK, result code "+str(rc))
    elif rc == 1:
        print ("Connection refused – incorrect protocol version")
    elif rc == 2:
        print("Connection refused – invalid client identifier")
    elif rc == 3:
        print("Connection refused – server unavailable")
    elif rc == 4:
        print("Connection refused – bad username or password")
    elif rc == 5:
        print("Connection refused – not authorised")
    else:
        print("Connected Failed, result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(CMDTOPIC)

def on_publish(client, userdata, mid):
    if DEBUG:
        print ("on_publish mid: ",mid)

def on_log(client, userdata, level, buf):
    if DEBUG:
        print("on_logging: ", level, buf)

def on_subscribe(client, userdata, mid, granted_qos):
    if DEBUG:
        print("Subscription acknowledged ")

def on_disconnect(client, userdata, rc):
    print("Disconnecting, Cleaning up GPIO.")
    GPIO.cleanup()
    client.loop_stop() #stop the loop

if __name__ == '__main__':
    # usage:
    #  python  hw_device.py  --debug --broker homeassistant.hm --user mqttuser --password mqttpass '

    parser = argparse.ArgumentParser(description='Hotwater MQTT device driver')

    parser.add_argument('--broker','-o',
                        type=str,
                        help='IP or name of MQTT broker' )
    parser.add_argument('--user','-u',
                        type=str,
                        help='Username for MQTT broker' )
    parser.add_argument('--password','-p',
                        type=str,
                        help='Password for MQTT broker' )
    parser.add_argument('--debug','-d',
                        action='store_true',
                        help='Enable Debug output.')
    args = parser.parse_args()

    if args.debug:
        print("debug on")
        DEBUG = args.debug

    if args.broker:
        MQTTbroker = args.broker

    if args.user:
        User = args.user

    if args.password:
        Password = args.password

    if DEBUG:
        print("Connecting to: ",MQTTbroker," User: ",User, " Password: ",Password, " Client", CLIENTID)

    # Setup the GPIO pins before the callbacks , Board numbering
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(power_pin, GPIO.OUT)

    client = mqtt.Client(CLIENTID)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_log = on_log
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish

    # home assistant has a user and a password set now
    client.username_pw_set(username=User, password=Password)
    client.connect(MQTTbroker, port=PORT)

    # send the message
    if DEBUG: print("Publishing ",DEVICESTATE," to topic",STATUSTOPIC)
    client.publish(STATUSTOPIC,DEVICESTATE)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop() #stop the loop
