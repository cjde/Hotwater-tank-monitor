#repo/py/HW_status.py
#repo/py/HW_temps.py
#repo/py/Calibration.json

cp repo/py/* /home/pi/hw
chmod +x  /home/pi/hw/HW_status.py
chmod +x  /home/pi/hw/HW_temps.py

# copy over the Web page directory
#repo/www/HW_temps.php
#repo/www/HW_status.php
#repo/www/hotwater.jpg
#
cp -r  repo/www/* /var/www/ceberry/hw
#
# Install the links if they are not there
#repo/sensors/1.upper
#repo/sensors/4.bottom
#repo/sensors/3.lower
#repo/sensors/2.middle
#
if ! ( -d  /home/pi/hw/sensors ); then
   cp -r --preserve=links repo/sensors /tmp/goo
fi
These files are copied into the working working directory on the pi that is also running a webserver

- py/HW_temps.py - Cron scheduled script that updates MQTT hotwater topic with a json structure containing temps and metadata about the waterheater
- py/hw_ctrl.py - Controller script on the webserver PI that communicates with the hot water PI to control power via a MQTT message

These files are installed on the Pi that is attached to the temperature sensoors that are attached to the hotwater heater

- py/HW_status.py - Main python script that collects the temperature data via a MQTT message from HW_temps.py
- py/hw_device.py - Daemon script running on the hotwater PI to respond to power control requests from hw_ctrl.py
- py/Calibration.json - Calabration data for the temperature sensors

- www/HW_status.php - PHP script that calls the HW_status.py to get the data from the hotwater pi and displays it
- www/script.js - implements that button callback for the power button
- www/gpio.php  - target of the javascript button push, calls the hw_ctrl.py to send the on off command to the MQTT topic hotwater/power
- www/poweroff.png - icon of the power button when off
- www/poweron.png - icon of the power button when on
- www/favicon.ico - iicon for the webpage ocon

 test scripts
D
D
- www/blinkled.php - call to the
- www/HW_temps.php


