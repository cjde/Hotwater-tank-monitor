__author__ = 'CJDE'
import re
from PIL import Image, ImageDraw, ImageFont
import requests
import json
import argparse
import sys

# this represents the colors from the maxtemp to 64 degrees less than the maxtemp.

TEMPCOLORS = ['#FF0000','#FF0008','#FF0010','#FF0018','#FF0020','#FF0028','#FF0030','#FF0038','#FF0040','#FF0048',
              '#FF0050','#FF0059','#FF0061','#FF0069','#FF0071','#FF0079','#FF0081','#FF0089','#FF0091','#FF0099',
              '#FF00A1','#FF00AA','#FF00B2','#FF00BA','#FF00C2','#FF00CA','#FF00D2','#FF00DA','#FF00E2','#FF00EA',
              '#FF00F2','#FF00FA','#FA00FF','#F200FF','#EA00FF','#E200FF','#DA00FF','#D200FF','#CA00FF','#C200FF',
              '#BA00FF','#B200FF','#AA00FF','#A100FF','#9900FF','#9100FF','#8900FF','#8100FF','#7900FF','#7100FF',
              '#6900FF','#6100FF','#5900FF','#5000FF','#4800FF','#4000FF','#3800FF','#3000FF','#2800FF','#2000FF',
              '#1800FF','#1000FF','#0800FF','#0000FF'
              ]
# this is the dictionary of converted color tuples with the tempcolors  mapped to the range that we expect to see in the
# tank we are expecting to see no more that a 64 degree temp differential from the top of the tank to the bottom. This
# dictionary is keyed by the temperature rounded to 1/COLOR_DIV degrees ( ie. "70.0", "70.2", "70.4"... )
TEMP_TO_COLOR ={}

# maximum temp expected in the tank ( must be greater that 64 )
MAXTEMP = 135
MINTEMP = MAXTEMP - len(TEMPCOLORS)

# Width of the image, Height is determined by the  size of the tank
MAP_WIDTH = 240

# color divisions per degree interpolated
COLOR_DIV = 4

# temp of the probes
PROBE_TEMP_LIST=[125,95,90,70]

# This is the distance from the top of the tank to the probe location ( in 10ths of an inch)
PROBE_DIST_LIST=[0, 170, 410, 530]

#shifts the heat map over for the legend and down so that it is centered
# this value has been determined based on the size of the font, any smaller and
# the legend will run over the heat map
SCALE_SHIFT=35

# tank volume 50 Gal
TANKSIZE = 50.0

# BTU energy to raise 1 lb of water 1 degree Fahrenheit
# 1 gallon of water weighs 8.34 lbs
# tank weight = 50 * 8.34
# tank is 53 in tall so tankweight/53 = weight per inch
LBS_PER_INCH = ( TANKSIZE * 8.34 )/ ( float(PROBE_DIST_LIST[-1] ) )

# temperature of the water flowing into the tank ( in degrees F )
ROOM_TEMP=74.0


# HWHEATER_URL = 'http://192.168.1.2/hw/HW_temps.php'
HWHEATER_URL = 'http://192.168.1.15/hw/HW_temps.php'

# right and left side of heat map labels
RSCALE={}
LSCALE={}

DEBUG = False; 

def hex2rgb (color):
    """
    :param color:  rgb color in "0xxxxxxx or #xxxxxx format that last six characters as assumed to be the color
    :return: rgb color tuple in integer format [255 128 0 ]
    """

    # split the six characters at the end  into each color component
    pattern = re.compile(r'.*(\w{2})(\w{2})(\w{2})')
    match = pattern.search(color)
    l = re.split(".(\w{2})(\w{2})(\w{2})",color)
    RRGGBB =  ( match.group(1), match.group(2), match.group(3) )
    rgb = [int(i,16) for i in RRGGBB ]
    return rgb

def rgb2hex(color):
    """
    This encodes a RGB tuple into a hex rgb format ( ie: #FFEEDD )
    :param color: Color in [R,G,B] format
    :return: Color in hex format
    """
    return '#'+''.join(map(chr,color )).encode('hex')

def save_rscale ( t, y ):
    """
    Called fro every temperature and saves the temp and the y coordinate of where that temp occurs for the first time
    :param t: temperature of the tank
    :param y: height of tank where it is that temperature
    :return:
    """
    # see if it is a multiple of 10
    got =  ( int( float(t)*10 ) % 100)
    if ( got == 0):
        # have we saved this temp before
        if t in RSCALE:
            # ignore it
            return
        else:
            RSCALE [t] = y


def interpolate_color( startcolor, endcolor, steps):
    """
    Generates the interpolation tuple that needs to be added to the start color "steps" number of times to
     get to the end color
    :param startcolor: Starting color tuple
    :param endcolor: Ending tuple
    :param steps:  number of interpolations to make between the start and end color
    :return: tuple of steps to make for each color band
    """
    return [(endcolor[i]-startcolor[i])/float(steps) for i in range(0,3)]


def interp_color_list(start_color, end_color, num_of_slices):
    """
    Generates a list of colors from one color to another, by add the interpolation steps to
    :rtype : object
    :param start_color: Start color
    :param end_color:   end color
    :param num_of_slices:
    :return: list of colors from start to (start + num_slices - 1)
    """
    color_list =[]
    interpol_step = interpolate_color( start_color,end_color,num_of_slices )
    # print "interpol_step",interpol_step
    for j in range( num_of_slices ):
        R = int( start_color[0] + (interpol_step[0]*j) )
        G = int( start_color[1] + (interpol_step[1]*j) )
        B = int( start_color[2] + (interpol_step[2]*j) )
        color_list.append([R,G,B])
    return color_list


def init_colormap(maxtemp=135):
    """
    This initializes the TEMP_TO_COLOR dictionary with the TEMPCOLORS color map, and then generates COLOR_DIV
    intermediate colors between each degree in the TEMP_TO_COLOR map.

    :param maxtemp: maximum temp of the tank It should be about 135 but we could adjust it lower in the winter
    :return: none modifies the public TEMP_TO_COLOR list with the
    """

    # set all the color slots to a shade of grey
    for i in range(maxtemp-64-5,maxtemp+5):
        t = "{0:.1f}".format( i * 1.0 )
        TEMP_TO_COLOR[t] = (i,i,i)

    # generate the color map for all temps in the range maxtemp to maxtemp-64
    # if we see a grey color on the color gradient then we know we have a over or under scale temp value

    for offset,item in enumerate(TEMPCOLORS):
        t = "{0:.1f}".format( ( maxtemp - offset) * 1.0 )
        TEMP_TO_COLOR[t] = hex2rgb(item)
        # dump the Temperature to color conversion table.
        # print maxtemp - offset, item ,t, TEMP_TO_COLOR[t]

    # generate COLOR_DIV colors between each temp
    for i in range(maxtemp-63,maxtemp):
        # format to a string with one decimal
        t1 = "{0:.1f}".format(i)
        t2 =   "{0:.1f}".format(i+1)
        # generate the interprolation colors
        tween = interp_color_list( TEMP_TO_COLOR[t1],  TEMP_TO_COLOR[t2], COLOR_DIV )
        k = 1
        # put the interpolated colors and there temps into the translation table
        while ( k < COLOR_DIV ):
            temp = "{0:.1f}".format(i + (k/(COLOR_DIV*1.0)))
            TEMP_TO_COLOR[temp] = tween[k]
            # print temp
            k += 1

def interp_xy_list(start,width,steps):
    """
    Generates a list of rectangles

    :param start: X,Y coordinate to start at
    :param width: width of
    :param steps:
    :return:
    """

    # generate the X1,Y1 X2,Y2
    # X1,X2 either 0 or the width of the bar
    x1 = SCALE_SHIFT
    x2 = MAP_WIDTH
    rect_list = []
    # Y1 is distance from the top + (the height of the segment * j )
    # Y2 is Y1 + a little more ( another step)
    for i in range( 0,steps ):
        y1 = int( start +  width * i )
        y2 = int( y1 + width )
        rect_list.append([ x1,y1,x2,y2])
    return rect_list

def render_color_map( t_list, d_list, outfile ):
    """
    This takes a list of probe temperatures and probe distances  and generates a temperature gradient map
    then saves that to the file name specified in outfile

    :rtype : object
    :param t_list: probe temperature list
    :param d_list: probe distance list
    :param outfile: output JPEG file name
    :return:
    """

    # the thing that we will draw in
    # it has a border at the left, right, top, bottom of SCALE_SHIFT so that the actual color map
    # is drawn in the middle of the graphic
    im = Image.new("RGB",(MAP_WIDTH+SCALE_SHIFT, d_list[-1]+SCALE_SHIFT+SCALE_SHIFT),"lightgrey")
    # print(im.format, im.size, im.mode)
    draw = ImageDraw.Draw(im)
    font = ImageFont.load_default()

    # make the left scale
    for probe_num in range( 0, len(d_list) ):
        t = "{0:.1f}".format( t_list[probe_num] * 1.0 )
        LSCALE[t] = d_list[probe_num] + SCALE_SHIFT

    # temperature rectangle height
    tankresolution = 1

#   we will need to go from the top of the tank to the bottom stepping 1unit of resolution at a time
    for probe_num in range( 0, len(d_list)-1 ):
        # 0
        d1 = d_list[probe_num]   + SCALE_SHIFT
        # 100
        d2 = d_list[probe_num+1] + SCALE_SHIFT
        # 100 - 0
        # so from one probe at the first distance to the next probe at the next distance we have to take this many steps
        tanksteps = int ( abs (d1 - d2 )  )
        # ok then we  need a list of tanksteps rectangles, starting from the first probe, each the resolution width,
        rect_list = interp_xy_list(d1,tankresolution,int(tanksteps))
        #print "d1, d2",d1,d2
        #print "tanksteps",tanksteps
        #print "rect_list",rect_list

        # now figure out the temp at each of these
        # take the temp differential and split it into the same number of parts
        # add a part each time, round to the nearest temp  and then look it up, and draw it
        t1 = t_list[probe_num]
        t2 = t_list[probe_num+1]

        # check out of range
        if t1 > MAXTEMP : t1 = MAXTEMP
        if t2 > MAXTEMP : t2 = MAXTEMP
        if t1 < MINTEMP : t1 = MINTEMP
        if t2 < MINTEMP : t2 = MINTEMP

        temp_delta = t1 - t2
        temp_increment = float( temp_delta * 1.0 / tanksteps * 1.0  )
        # print "temp_delta",temp_delta
        # print "temp_increment",temp_increment

        temp_count = 0.0
        for rect in rect_list:
            temp_here = t1 + temp_count
            # round the temp_here to the nearest COLOR_DIV
            t = "{0:.1f}".format(round(temp_here * COLOR_DIV, 0 )/COLOR_DIV)


            # dont fall off the end of hte color map  
            if int(temp_here) == MINTEMP : 
                safe_t = "{0:.1f}".format( MINTEMP)
                draw.rectangle(rect,fill=rgb2hex(TEMP_TO_COLOR[safe_t]))
            else:
                draw.rectangle(rect,fill=rgb2hex(TEMP_TO_COLOR[t]))
                safe_t = t 

            if DEBUG: 
                #sys.stderr.write( "t: %s rect[Y1]: %d\n" % ( t,  rect[1] )) 
                print t,rect,TEMP_TO_COLOR[safe_t]

            # print temp along the side of the color map every 10 degrees
            # make a list of all the points where the the temperature ends in 0
            # ( basicly every 10 degrees )
            save_rscale ( t, rect[1] )

            temp_count -= temp_increment
    #
    # put the right scale on the graph RSCALE has the temp->height pairs
    for y in RSCALE:
        draw.text( (MAP_WIDTH+3,RSCALE[y]), y, font=font, fill="black")

    # put the left scale on the graph
    for y in LSCALE:
        draw.text( (3,LSCALE[y]), y, font=font, fill="black")
        # print LSCALE[y], y


    del draw
    # only draw the color map on the windows test system
    if ( sys.platform == "win32" ):
        im.show()

    # always write the picture to a file
    im.save(outfile,"JPEG", quality=90,optimize=True) # , progressive=True)

def get_hotwater_data0():
    """
    This is the function that gets the data from the other pi that is actually monitoring the HW heater
    Stored at the URL is structure that represents the 4 probes that are attached to the tank.
    The structure has extra data that we dont need so we just pull out the stuff that in important
    """
    r = requests.get(HWHEATER_URL)
    dic = json.loads( r.text )
    PROBE_TEMP_LIST = [i["temp_f"] for i in dic ]
    PROBE_DIST_LIST = [i["dist"] for i in dic ]

    #print json.dumps(PROBE_TEMP_LIST,sort_keys=False,indent=4,separators=(',', ': '))

    return PROBE_TEMP_LIST, PROBE_DIST_LIST

import paho.mqtt.client as mqtt
PAYLOAD = "" 

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hotwater")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global PAYLOAD
#    print(msg.topic+" "+str(msg.payload))
    PAYLOAD = str(msg.payload) 
    client.disconnect()


def get_hotwater_data():
    """
    This is the function that gets the data from the other pi that is actually monitoring the HW heater
    Stored at the URL is structure that represents the 4 probes that are attached to the tank.
    The structure has extra data that we dont need so we just pull out the stuff that in important
    """
    global PAYLOAD

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.2.48", port=1883, keepalive=60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
    # this will return when the call back disconnets and the PAYLOAD global has been filled 

    dic = json.loads( PAYLOAD )
    PROBE_TEMP_LIST = [i["temp_f"] for i in dic ]
    PROBE_DIST_LIST = [i["dist"] for i in dic ]

#    print json.dumps(PROBE_TEMP_LIST,sort_keys=False,indent=4,separators=(',', ': '))

    return PROBE_TEMP_LIST, PROBE_DIST_LIST

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


def dev_test ():
    # just some testing to make sure we get what we think we should

    # Break up the hex color into a 3tuple color
    [a,r,g,b,z] = re.split("..(\w{2})(\w{2})(\w{2})","0xFF0000")
    print "argbz:",a,r,g,b,z
    rgb = [ int( r,16 ),int( g,16 ), int( b,16 ) ]
    print "rgb1", rgb

    # an alternate way
    l = re.split("..(\w{2})(\w{2})(\w{2})","0xFF0000")
    print  "split list",l
    print l[1], l[2], l[3]
    rgb = [ int( (l[1]),16 ),int( (l[2]),16 ), int( (l[3]),16 ) ]
    print "rgb",rgb

    # get at 3tuple made out of the last six characters in the color
    pattern = re.compile(r'.*(\w{2})(\w{2})(\w{2})')
    match = pattern.search("0xFF8800")
    RRGGBB =  ( match.group(1), match.group(2), match.group(3) )
    rrggbb = [int(i,16) for i in RRGGBB ]
    print "rrggbb",rrggbb

    # test for the interpolate
    interp = interpolate_color( [10, 0, 255],   [0, 20, 255] , 10 )
    print "interpolation steps: should be [-1.0 2.0 0],", interp
    #for key in sorted(TEMP_TO_COLOR.keys()):
    #    print key, TEMP_TO_COLOR[key]
    testtemp = "{0:.1f}".format(MAXTEMP)
    print "color at  :",testtemp,TEMP_TO_COLOR[testtemp]
    testtemp = "{0:.1f}".format(MAXTEMP+1)
    print "overscale color at  :",testtemp,TEMP_TO_COLOR[testtemp]

    # test for interpolate color list
    print interp_color_list([10,10,10], [5,20,100], 10)

    # File name to generate colormap
    dest = "c:\\temp\\hotwater1.jpeg"
    #render_color_map (PROBE_TEMP_LIST, PROBE_DIST_LIST, dest)

    dest = "c:\\temp\\hotwater2.jpeg"
    PROBE_TEMP_LIST=[125,95,100,73,90,70]
    PROBE_DIST_LIST=[0, 170, 410, 530, 700, 800]
    # render_color_map (PROBE_TEMP_LIST, PROBE_DIST_LIST, dest)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Hotwater temp probe')

    parser.add_argument('--outfile',
                        '-o',type=str,
                        help='Output file name' )
    parser.add_argument('--nomap','-n',
                        action='store_true',
                        help='do not generate a heat map only output the heat content')
    parser.add_argument('--debug','-d',
                        action='store_true',
                        help='Enable Debug output.')

    args = parser.parse_args()

    if args.outfile:
        dest = args.outfile
    else:
        # windows or Linux file name
        if ( sys.platform == "win32" ):
            dest = "c:\\temp\\hotwater.jpeg"
        else:
            dest = "/tmp/hotwater.jpg"

    if args.debug: 
       DEBUG = True
       sys.stderr.write( "Debug enabled\n" )


    # Get the temperature from the Pi that is monitoring the hotwater heater
    PROBE_TEMP_LIST, PROBE_DIST_LIST =  get_hotwater_data()

    # calculate energy content
    BTU, KWH, KJ = heatcontent (PROBE_TEMP_LIST, PROBE_DIST_LIST )
    BTU_str = "{0:.0f}".format(BTU)
    KWH_str = "{0:.1f}".format(KWH)
    KJ_str = "{0:.0f}".format(KJ)
    # also 1 watt is 1 J/sec
    # so if the tank heats up by 1000J in 1 sec that takes 1000j/(1/3600 hour)  or 1KWS
    # 1KWH / 3600*KWS  or  1KWS = .278KWh


    if args.nomap:
        jsonout = { "BTU":BTU_str, "KWH":KWH_str, "KJ":KJ_str }
        print json.dumps(jsonout,sort_keys=False,indent=4,separators=(',', ': '))
    else:
        jsonout = { "BTU":BTU_str, "KWH":KWH_str, "KJ":KJ_str, "temp_listf":PROBE_TEMP_LIST }
        print json.dumps(jsonout,sort_keys=False,indent=4,separators=(',', ': '))

        # map the colors in the color map to the range of temps that we expect in the tank
        init_colormap(MAXTEMP)

        # run some tests
        # dev_test()

        # generate the color map for the
        render_color_map (PROBE_TEMP_LIST, PROBE_DIST_LIST, dest)





