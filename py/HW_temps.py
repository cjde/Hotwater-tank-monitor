__author__ = 'CJDE'
import os
import glob
import time
import re
import json
import argparse
import sys

# this is the list of sensors and associated properties that make up the hot water heater
SENSORS  = []

# where the calibration file is at These values are used to correct minor variances in the readings toe each probe
CALFILE = "Calibration.json"

# This is the distance from the top of the tank to the probe location ( in 10ths of an inch)
# this may be good to read from a config file ....
PROBE_DIST_LIST=[0, 170, 410, 530, 600,700]

# By default we will be running running on the Rpi but for testing purposed this flag ( passed in from the commandline)
# allows us to code around the kernel set up that is done on the pi.
SIMULATE=False

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

    temp_c = round ( C/2.0,4 )
    temp_f = temp_c * 9.0 / 5.0 + 32.0
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
                print '{0:10s} Raw:{1:5.1f} Cal_factor:{2:5.2f} Cooked_temp{3:6.1f} sample:{4:5.2f}'.format\
                    (label, deg_c, SENSORS[i]["calibration"],SENSORS[i]["temp_c"], SENSORS[i]["num_readings"] )

            time.sleep(3)

        # dump the calibration string to a file
        for i in range( 0, 4 ):
            CAL.append( SENSORS[i]["calibration"] )

        print "saving new calibrations: to ",CALFILE, CAL
        f = open(CALFILE, 'w')
        json.dump(CAL,f,sort_keys=True,indent=4,separators=(',', ': ') )
        f.close()



# Main function
# Description:
#   Uses the list of devices it queries them one by one, calculates the average and the delta each sensor is from the average
#   This delta values will be used to calabrate each sensor


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


args = parser.parse_args()

if args.calibrate:
    CALIBRATE = args.calibrate
else:
    CALIBRATE = 0


if ( args.simulate or  sys.platform == "win32" ):
    SIMULATE = True
else:
    # Running on PI
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    SIMULATE = False

# get the list of temp probes  attached to the bus
base_dir = '/home/pi/hw_heater/sensors/'
dev_name = '/w1_slave'
# for example ... /home/pi/hw_heater/sensors/1.upper/w1_slave' They are links to the real device files but by creating
# links we can assign them a name and an ordinal value. prob0 is at the top probe prob3 is at the bottom

DEV_FILES = sorted( glob.glob( base_dir + '*' + dev_name) )

pat = re.compile( '/home/pi/hw_heater/sensors/(.*)/w1_slave')
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
    #print '{0:20s} Raw_temp{1:5.1f} Cooked_temp_c{2:5.1f} Cooked_temp_f{3:5.1f} Calibration{4:5.1f}'\
    #    .format(label, deg_c, SENSORS[i]["temp_c"], SENSORS[i]["temp_f"], SENSORS[i]["calibration"])

# short or long form
if args.verbose:
    SENSORS_str = json.dumps(SENSORS,sort_keys=True,indent=4,separators=(',', ': '))
    print SENSORS_str
else:
    print [SENSORS[i]["temp_f"] for i in range( 0, len(DEV_FILES) ) ]








