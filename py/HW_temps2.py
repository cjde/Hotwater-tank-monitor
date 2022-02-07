"""
Description: 
 Collects temps fro mthe hotwater heater and publish them to the MQTT message queue 
 
 Mod: 10/21/17 - changed MQTT server to 192.168.2.48 
"""
__author__ = 'CJDE'
import os
import glob
import time
import re
import json
import argparse
import sys
import paho.mqtt.client as mqtt

MQTTbroker = "homeassistant.hm"
User = "mqttuser"
Password = "mqttpass"
PORT = 1883
myhost = os.uname()[1]
client_id = "hotwater-v2_temps" + "-" +  myhost
STATUSTOPIC =  "hotwater-v2/temps"

DEBUG = ""

# this is the list of sensors and associated properties that make up the hot water heater
SENSORS  = []

# where the calibration file is at These values are used to correct minor variances in the readings toe each probe
CALFILE = "Calibration.json"

# This is the distance from the top of the tank to the probe location ( in 10ths of an inch)
# this may be good to read from a config file ....
PROBE_DIST_LIST=[0, 170, 410, 530]

# tank volume 50 Gal
TANKSIZE = 50.0

# BTU energy to raise 1 lb of water 1 degree Fahrenheit
# 1 gallon of water weighs 8.34 lbs
# tank weight = 50 * 8.34
# tank is 53 in tall so tankweight/53 = weight per inch
LBS_PER_INCH = ( TANKSIZE * 8.34 )/ ( float(PROBE_DIST_LIST[-1] ) )

# temperature of the water flowing into the tank ( in degrees F )
ROOM_TEMP=74.0

# By default, we will be running running on the Rpi but for testing purposed this flag
# ( passed in from the commandline) allows us to code around the kernel set up that is done on the pi.
SIMULATE=False
BASE_DIR = '/home/pi/Hotwater-tank-monitor/sensors/'
BASE_DIR_SIM = '/home/pi/Hotwater-tank-monitor/sensors.sim/'

# list of device files, basically the number of temperature probes
DEV_FILES=[]


def read_temp_raw(dfile):
    """
    # This function just gets the two lines that the sensor returns when queried.
    # the temperature data returned looks like this:
    #    c4 01 4b 46 7f ff 0c 10 3b : crc=3b YES
    #    c4 01 4b 46 7f ff 0c 10 3b t=28250
    """
    f = open(dfile, 'r')
    lines = f.readlines()
    f.close()
    return lines



def read_temp( dfile ):
    """
    This function gets the temp from the sensor and retries if the device is not ready
    it returns the temp in Centigrade and in Fahrenheit.
    """
    C = 0
    # Get the temp from the sensor  twice in a row and then average it
    for sample in range(0,2):
        lines = read_temp_raw( dfile )
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw(dfile)

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            C = float(temp_string) / 1000.0 + C

    temp_c = round ( C/2.0,1 )
    temp_f = round ( temp_c * 9.0 / 5.0 + 32.0,1 )
    return temp_c, temp_f

def do_calibration(cal_loop=10 ):
    """
    This is the calibration function. To use it all the temp probes must be in the test bed. Given that they
    are all together it is reasonable to assume that they should all be the same temperature. The calibration
    is based on the a static difference between the first probe and all the others. The difference from probe 0
    is calculated for each probes[1..n] and is added to the raw value so that each probe is the same as the
    first probe
    """

    CAL = []
#   If the calibration loop is 0 then use previously determined values
    if cal_loop == 0:
        # look to see if the calibration file is there
        if os.path.isfile(CALFILE):
            # Good go slurp it up
            f = open(CALFILE, 'r')
            # load it into the Calibration structure
            CAL = json.load( f )
            f.close()
            # should check to see if the size of the calibration file is the same length as the device file
            #print "CAL type/ data",type(CAL),CAL
            for i in range( 0, len(DEV_FILES) ):
                SENSORS[i]["calibration"] = CAL[i]
        else:
            #print "No calibration file :", CALFILE, " setting to zero"
            for i in range( 0,  len(DEV_FILES) ):
                SENSORS[i]["calibration"] = 0.0

    else:
        # run the calibration loop
        for cal_count_loop in  range(1,cal_loop+1):

            # get the temp of each probe
            for i in range( 0,   len(DEV_FILES) ):

                label =  SENSORS[i]["label"]
                deg_c, deg_f = read_temp(  SENSORS[i]["device"] )
                # set up probe 0 as the baseline probe
                if ( i == 0 ):
                    ref_temp = deg_c
                else:
                    ref_temp = SENSORS[0]["temp_c"]
                # the number and sum of the differences is collected
                SENSORS[i]["num_readings"] += 1
                SENSORS[i]["sum_readings"] += ref_temp - deg_c
                # the calibration factor is the average of the differences
                SENSORS[i]["calibration"] = round( SENSORS[i]["sum_readings"] / SENSORS[i]["num_readings"],4 )
                # the temp of the probe is the temp from the sensor + the calibration
                SENSORS[i]["temp_c"] = deg_c + SENSORS[i]["calibration"]
                SENSORS[i]["temp_f"] = SENSORS[i]["temp_c"] * 9.0 / 5.0 + 32.0
                #print ( {0:10s} Raw:{1:5.1f} Cal_factor:{2:5.2f} Cooked_temp{3:6.1f} sample:{4:5.2f}'.format
                #    (label, deg_c, SENSORS[i]["calibration"],SENSORS[i]["temp_c"], SENSORS[i]["num_readings"] )

            time.sleep(3)

        # dump the calibration string to a file
        for j in range( 0, 4 ):
            CAL.append( SENSORS[j]["calibration"] )

        print ("saving new calibrations: to ",CALFILE, CAL)
        f = open(CALFILE, 'w')
        json.dump(CAL,f,sort_keys=True,indent=4,separators=(',', ': ') )
        f.close()



def gettemps( base_dir = BASE_DIR ):

    global DEV_FILES, DEBUG
    # get the list of temp probes  attached to the bus

    dev_name = '/w1_slave'
    # for example ... /home/pi/hw_heater/sensors/1.upper/w1_slave' They are links to the real device files but by creating
    # links we can assign them a name and an ordinal value. prob0 is at the top probe prob3 is at the bottom

    DEV_FILES = sorted( glob.glob( base_dir + '*' + dev_name) )

    pat = re.compile( base_dir +'(.*)/w1_slave')
    for i in range( 0,  len(DEV_FILES) ):
        # just in case we are running in simulation mode an we have DOS file names!!
        dev = DEV_FILES[i].replace('\\','/')
        match = pat.search(dev)
        l = match.group(1)
        # initialize the device file, label, and initial calibration value
        #  the one point calibration does not seem to be working, the same probe at the same temerature seems to be be a different value each time
        # the probes donr seem to be a constant
        # difference in temperature apart
        SENSORS.append( { "device":dev, "label":l, "calibration":0.0, "num_readings":0,
                          "sum_readings":0,"temp_c":0.0,"temp_f":0.0, "dist":PROBE_DIST_LIST[i] })

    # run the calibration loop
    do_calibration( CALIBRATE )

    #Get the temp and apply the calibration to it
    for i in range( 0,  len(DEV_FILES) ):
        label =  SENSORS[i]["label"]
        deg_c, deg_f = read_temp(  SENSORS[i]["device"] )
        SENSORS[i]["temp_c"] = deg_c + SENSORS[i]["calibration"]
        SENSORS[i]["temp_f"] = SENSORS[i]["temp_c"] * 9.0 / 5.0 + 32.0
        if DEBUG:
            print ( '{0:20s} Raw_temp{1:5.1f} Cooked_temp_c{2:5.1f} Cooked_temp_f{3:5.1f} Calibration{4:5.1f}'\
            .format(label, deg_c, SENSORS[i]["temp_c"], SENSORS[i]["temp_f"], SENSORS[i]["calibration"]) )

    return SENSORS

def heatcontent (t_list, d_list ):
#     """
#     calculates the heat content for each temperature band in the tank
#     :param t_list: temperature at the probes
#     :param d_list: distance from top of tank to each of the probes
#     :return: BTU in the entire tank
#     """

    # figure out how many BTU is in each slice
    BTU = 0.0
    for probe_num in range( 0, len(d_list)-1):
        d1 = d_list[probe_num]
        d2 = d_list[probe_num+1]
        # inches in this sliace
        slice_height = d2 - d1;

        t1 = t_list[probe_num]
        t2 = t_list[probe_num+1]
        # temp of the input water ( subtract off  the room temp component )
        avg_temp_increase = ((t1 + t2 )/2.0 ) - ROOM_TEMP

        # we already figured ou how many lbs of water are in are in a inch of tank
        # so the number of BTU = weight of water * Temp delta
        BTU += float( slice_height * LBS_PER_INCH ) * avg_temp_increase
        # print BTU
    # 1 KWH = 3412.14 BTU
    # or
    # 1KWH = 3600 Kjoules/hour
    KWH = BTU/3412.14
    # 1 KJ = 0.947817 BTU
    KJ = BTU/0.947817

    return BTU,KWH,KJ

if __name__ == '__main__':
# Main function
# Description:
#   Uses the list of devices it queries them one by one, calculates the average and the delta each sensor is from the average
#   This delta values will be used to calibrate each sensor

    parser = argparse.ArgumentParser(description='Hotwater temp probe')

    parser.add_argument('--verbose','-v',
        action='store_true',
        help='verbose flag' )

    parser.add_argument('--calibrate',"-c",
        type=int,
        default=0,
        help='Calculate calibration offsets. A value of 0 will load the defaults' )

    parser.add_argument('--simulate','-s',
        action='store_true',
        help='simulate the device files instead of using the ones on the PI' )

    parser.add_argument('--test_calibration','-t',
        type=int,
        default=0,
        help='Number or temp collections to run and apply the calibration amount ' )

    parser.add_argument('--debug', '-d',
        action='store_true',
        help='Enable Debug output.')

    parser.add_argument('--mqtt','-m',
        action='store_true',
        help='Publish to MQTT server' )

    parser.add_argument('--broker', '-o',
        type=str,
        help='IP or name of MQTT broker')

    parser.add_argument('--user', '-u',
        type=str,
        help='Username for QQTT broker')

    parser.add_argument('--password', '-p',
                        type=str,
                        help='Password for MQTT broker')

    args = parser.parse_args()

    if args.calibrate:
        CALIBRATE = args.calibrate
    else:
        CALIBRATE = 0

    if args.simulate or  sys.platform == "win32":
        base_dir = BASE_DIR_SIM
        SIMULATE = True
    else:
        # Running on PI
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = BASE_DIR
        SIMULATE = False

    if args.debug:
        print("Debug on")
        DEBUG = args.debug

    SENSORS = gettemps( base_dir )

    # calculate energy content
    # Pull it back out of the dictionary in case it got adjusted somewhere
    PROBE_TEMP_LIST = [i["temp_f"] for i in SENSORS]
    PROBE_DIST_LIST = [i["dist"] for i in SENSORS]

    btu, kwh, kj = heatcontent (PROBE_TEMP_LIST, PROBE_DIST_LIST )
    # given:  1 watt is 1 J/sec
    # so if the tank heats up by 1000J in 1 sec that takes 1000j/(1/3600 hour)  or 1KWS
    # 1KWH / 3600*KWS  or  1KWS = .278KWh

    SENSORS.append ( {"KWH" : "{0:.1f}".format(kwh),"KJ" :"{0:.0f}".format(kj), "BTU" : "{0:.0f}".format(btu) } )

    # short or long form
    if args.verbose:
        SENSORS_str = json.dumps(SENSORS,sort_keys=True,indent=4,separators=(',', ': '))
    else:
        #print [SENSORS[i]["temp_f"] for i in range( 0, len(DEV_FILES) ) ]
        SENSORS_str = json.dumps([SENSORS[i]["temp_f"] for i in range( 0, len(DEV_FILES) ) ],sort_keys=True,indent=4,separators=(',', ': '))

    if DEBUG: print (  SENSORS_str )

    if args.mqtt:
        client = mqtt.Client(client_id)
        client.username_pw_set(username=User, password=Password)
        client.connect(MQTTbroker, port=PORT)
        # insert discovery publish here
        client.publish( STATUSTOPIC, SENSORS_str, qos=1, retain=True )
        client.disconnect()





