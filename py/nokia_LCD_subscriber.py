import paho.mqtt.client as mqtt
import json
import re
import argparse
import nokia_lcd

# message from MQTT ( in "byte" format )
PAYLOAD = ''
DEBUG = ""
CMDTOPIC = "hotwater-v2/nokia_lcd/cmd"
STATUSTOPIC =  "hotwater-v2/nokia_lcd/status"
CLIENTID  = "nokia_lcd"
PORT = 1883
ON_MSG     = 'ON'
OFF_MSG    = 'OFF'
STATUS_MSG = 'GET'
LCDSTATE  = "Unknown"
MQTTbroker = "homeassistant.hm"
User = "mqttuser"
Password = "mqttpass"
client_id = "nokia_lcd"
MAXTIMEOUT = 60




#
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
    if  rc==0 :
        print("Connected OK, result code "+str(rc))
    else:
        print("Connected Failed, result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(CMDTOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # valid JSON message format
    # [{"linenum": 0, "msg": "BTU: 17023","backlight":1}]

    global PAYLOAD,LCDSTATE

    PAYLOAD = msg.payload

    if args.debug:
        print("Got message topic: ", msg.topic + " Payload: " + str(PAYLOAD))

    # check if it is a off or on message from homeassistant. Light devices send just byte codws
    try:
        decoded = msg.payload.decode('UTF-8')
        if decoded == ON_MSG:
            if DEBUG:
                print("ON")
            nokia_lcd.backlight( True )
            LCDSTATE = decoded
        elif decoded == OFF_MSG:
            if DEBUG:
                print("OFF")
            nokia_lcd.backlight( False )
            LCDSTATE = decoded
        elif decoded == STATUS_MSG:
            if DEBUG:
                print("STATUS")
            if DEBUG: print("Publishing ", LCDSTATE, " to topic", STATUSTOPIC)
            client.publish(STATUSTOPIC, LCDSTATE)
        else:
            # check if it is JSON data
            try:
                dic = json.loads(decoded)
            except ValueError as e:
                print ("Bad JSON message: ",str(PAYLOAD))
                client.publish(STATUSTOPIC, "Bad JSON message")
                return False

            # save the state for the next time
            LCDSTATE = decoded
            if DEBUG:
                print ("JSON payloads:",len(dic) )
                print ("Got data from MQTT:","line:",dic[0]["linenum"], "msg:",dic[0]["msg"],"light:",dic[0]["backlight"] )
            for msgid in range(len(dic)):
                nokia_lcd.write( dic[msgid]["linenum"], dic[msgid]["msg"], dic[msgid]["backlight"] )

        return True

    except:
        print ("Bad data in binary message: ",str(PAYLOAD))
        return False

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
        print("Unexpected disconnect code: ", rc)


if __name__ == '__main__':
    # usage:
    #  python  nokia_LCD_subscribe.py  --debug --broker homeassistant.hm --user mqttuser --password mqttpass '

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
    args = parser.parse_args()

    if args.broker:
        print("broker", args.broker )
        MQTTbroker = args.broker

    if args.user:
        print("User", args.user )
        User = args.user

    if args.password:
        print("Pass", args.password )
        Password = args.password

    if args.debug:
        print("debug on")
        DEBUG = args.debug

    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_log = on_log
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish

    if DEBUG:
        print("Connecting to: ",MQTTbroker," User: ",User, " Password: ",Password)

    client.username_pw_set(username=User, password=Password)
    client.connect(MQTTbroker, port=PORT)

    # send a test message
    if DEBUG: print("Publishing ",LCDSTATE," to topic",STATUSTOPIC)
    client.publish(STATUSTOPIC,LCDSTATE)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        nokia_lcd.backlight(False)
        client.loop_stop() #stop the loop
        client.disconnect()


