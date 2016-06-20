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
