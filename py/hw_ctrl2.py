"""
This is the command line tool that is used to send on and off commands to the hot water PI
The commands to turn on, off and get ( the current state )  are

python hw_ctrl.py -n
python hw_ctrl.py -f
python hw_ctrl.py -g



"""

import paho.mqtt.client as mqtt
import json
import re
import argparse
import time



# message from MQTT ( in "byte" format )
PAYLOAD = ''
DEBUG = ""
CMDTOPIC   =  "hotwater-v2/power"
STATUSTOPIC = "hotwater-v2/status"
CLIENTID   = "hw_controller2"
PORT = 1883
# Retries for a GET responce from the heater
MAXRETRY = 10
ON_MSG     = 'ON'
OFF_MSG    = 'OFF'
STATUS_MSG = 'GET'
DEVICESTATE  = "Unknown"
BADJSON = "-1"
MQTTbroker = "homeassistant.hm"
User = "mqttuser"
Password = "mqttpass"


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

        if decoded == ON_MSG :
            if DEBUG: print("ON")
            DEVICESTATE = decoded
        elif decoded == OFF_MSG :
            if DEBUG: print("OFF")
            DEVICESTATE = decoded
        elif decoded == "Unknown" :
            if DEBUG: print("Unknown")
            DEVICESTATE = decoded
        elif decoded == BADJSON :
            if DEBUG: print("Hotwater has recieved bad JSON data.")
            DEVICESTATE = decoded
        else:
            print ("Unknown responce to a GET message:")
            return False
    except:
        print ("Cannot decode message from hotwater: ",str(PAYLOAD))
        return False
    return True

def on_connect(client, userdata, flags, rc):
    """
    Subscribes to the hotwater topic and prints the message
    The callback for when the client receives a CONNACK response from the server.
    """
    if  rc == 0 :
        if DEBUG: print("Connected OK, result code "+str(rc))
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
    ### ? client.subscribe(CMDTOPIC)

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
    if rc != 0:
        print("Unexpected disconnection.")

if __name__ == '__main__':

    # default command is GET
    cmd = STATUS_MSG
    parser = argparse.ArgumentParser(description='Nokia LCD subscription ')

    parser.add_argument('--broker','-o',
                        type=str,
                        help='IP or name of MQTT broker' )
    parser.add_argument('--user','-u',
                        type=str,
                        help='Username for QQTT broker' )
    parser.add_argument('--password','-p',
                        type=str,
                        help='Password for MQTT broker' )
    parser.add_argument('--debug','-d',
                        action='store_true',
                        help='Enable Debug output.')
    parser.add_argument('--on','-n',
                        action='store_true',
                        help='Send ON Command.')

    parser.add_argument('--off','-f',
                        action='store_true',
                        help='Send off Command.')

    parser.add_argument('--get','-g',
                        action='store_true',
                        help='Get status.')

    parser.add_argument('--homeassist','-ha',
                        action='store_true',
                        help='Output ON,OFF, Unknown status instead of numeric')

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

    if args.on:
        cmd = ON_MSG
    if args.off:
        cmd = OFF_MSG
    if args.get:
        cmd = STATUS_MSG

    if DEBUG:
        print("Connecting to: ",MQTTbroker," User: ",User, " Password: ",Password, " Client", CLIENTID)

    # since this is a user tool remove this all info about this client when done
    client = mqtt.Client(CLIENTID,clean_session=True)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_log = on_log
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish


    client.username_pw_set(username=User, password=Password)
    client.connect(MQTTbroker, port=PORT)

    # set up listener if getting status
    if cmd == STATUS_MSG:
        # clear any old messages and subscribe to the status topic
        if DEBUG:  print("Starting subscription to:", STATUSTOPIC)
        client.subscribe(STATUSTOPIC, 1)

    # start the asyc listener loop
    client.loop_start()
    # send the message
    if DEBUG: print("Publishing ",cmd," to topic",CMDTOPIC)
    client.publish(CMDTOPIC,cmd)


    # Wait for the responce if the command was a GET
    if cmd == STATUS_MSG:
        timeout = 0
        while DEVICESTATE == "Unknown" and timeout < MAXRETRY:
            time.sleep(.1)
            timeout += 1
            if DEBUG: print("Waiting for status ", DEVICESTATE, timeout)

        # Ok got a responce from the GET, is this output for home assitant or the old PHP page
        if not args.homeassist:
            if DEVICESTATE == ON_MSG: print( "1" )
            elif DEVICESTATE == OFF_MSG:   print( "0" )
            else: print( "-1" )
        else:
            print (DEVICESTATE)

    client.loop_stop()
    client.disconnect()

