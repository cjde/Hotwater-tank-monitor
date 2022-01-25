# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This demo will fill the screen with white, draw a black box on top
and then print Hello World! in the center of the display

This example is for use on (Linux) computers that are using CPython with
Adafruit Blinka to support CircuitPython libraries. CircuitPython does
not support PIL/pillow (python imaging library)!
"""

import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_pcd8544
import time
import syslog


# Parameters to Change
BORDER = 1
FONTSIZE = 10
DISPLAYENABLED = False
SPACING = 1
display = ''
draw    = ''
image   = ''

# buffer for what is displayed on the little screen
scrbuf =[
    {"x1":1,"y1":2, "x2":3, "y2":4,"text":"","font":""},
    {"x1":1,"y1":2, "x2":3, "y2":4,"text":"","font":""},
    {"x1":1,"y1":2, "x2":3, "y2":4,"text":"","font":""},
    {"x1":1,"y1":2, "x2":3, "y2":4,"text":"","font":""}
]

syslog.openlog("nokia_lcd")

def backlight ( status ):
    # turn the backlight on or off  1 or 0
    global DISPLAYENABLED
    global display, draw, image

    if not DISPLAYENABLED:
       display, draw, image = setupLCD()

    blight = digitalio.DigitalInOut(board.D13)  # backlight
    blight.switch_to_output()
    if status==1 :
       blight.value = True
    else:
       blight.value = False
    #display.show()


def setupLCD ():
    # initial LCD setup and border

    global DISPLAYENABLED

    spi = busio.SPI(board.SCK, MOSI=board.MOSI)
    dc = digitalio.DigitalInOut(board.D6)  # data/command
    cs = digitalio.DigitalInOut(board.CE0)  # Chip select
    reset = digitalio.DigitalInOut(board.D5)  # reset

    display = adafruit_pcd8544.PCD8544(spi, dc, cs, reset)

    # Contrast and Brightness Settings
    display.bias = 5
    display.contrast = 40

    # Clear display.
    display.fill(0)
    display.show()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new("1", (display.width, display.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black background
    draw.rectangle((0, 0, display.width, display.height), outline=255, fill=255)

    # Draw a smaller inner rectangle
    draw.rectangle(
        (BORDER, BORDER, display.width - BORDER - 1, display.height - BORDER - 1),
        outline=0,
        fill=0,
    )
    DISPLAYENABLED = True
    #print ( " LCD setup done")
    return display, draw, image


def write( linenum, msg, bklight ):
    # at the specified linenum write the message

    global display, draw, image
    #print (" lcd.write linenum:", linenum, " msg: >", msg,"<")

    if not DISPLAYENABLED:
       display, draw, image = setupLCD()


    # Coords to place the text,
    x1 =  BORDER + 1
    scrbuf[linenum]["x1"] = x1
    scrbuf[linenum]["x2"] = display.width - BORDER -1

    y1 = BORDER + (FONTSIZE+1)*(linenum)
    scrbuf[linenum]["y1"] = y1
    scrbuf[linenum]["y2"] = y1 + FONTSIZE +1

    # is somethin is already there, erase it before new string
    if ( scrbuf[linenum]["text"] ):
        #print (" erase text 1 ")
        draw.text( (x1,y1 ),scrbuf[linenum]["text"],font=scrbuf[linenum]["font"], fill=0 )
    else:
        # Load the TTF font, maybe each line is a different font in the future?
        #print (" laod Font ")
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)
        (font_width, font_height) = font.getsize(scrbuf[linenum]["text"])
        scrbuf[linenum]["font"] = font

    # ok an the next line is...
    #print(" Draw text 1 ")
    draw.text( (x1,y1 ),msg,font=scrbuf[linenum]["font"] , fill=255 )
    # keep it for next time
    scrbuf[linenum]["text"] = msg

    # turn on the Backlight?
    if ( bklight==1 ):
        backlight ( True )
    else:
        backlight ( False )

    display.image(image)
    display.show()

if __name__ == '__main__':

    if not DISPLAYENABLED:
       display, draw, image = setupLCD()

    backlight(1)

    # scroll a couple lines on the screen
    l = [ 0,1,2,3 ]
    for i in range(5):
        write(l[0], "AAAAAAAAAAAAAA",1 )
        write(l[1], "BBBBBBBBBBBBBB",1 )
        write(l[2], "CCCCCCCCCCCCCC",1 )
        write(l[3], "DDDDDDDDDDDDDD",1 )

        time.sleep( .75 )
        s = l.pop(3)
        l.insert( 0,s )

    backlight(0)

