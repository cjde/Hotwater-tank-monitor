# Hotwater tank monitor

This is a hotwater tank monitoring applicaition. Attached to the A/C unit is a heat recovery unit. This provides hotwater through out the summer months. There is a Pi Zero that has 4 DS18B20 Digital temperature sensor (1 wire bus) that monitor the temperature of the tank at various points. These values are collected every minute and sent (via MQTT) to a PI "B" that is running MRTG ( and associated Web and DB ). The Pi"B" computes various energy components and the heat map of the tank. This goes into a very crude display ( mainly a PHP learning project ) to serve up to browsers.

The PI zero has reciently been equipped with at 12V SPDT relay attached to pin 26 ( with a 2N2222 ). This double pole relay is the power control to both phases of 240V main for the heater. The the python script hw_driver.py  listens on the MQTT bus for the the topics hotwater/power with messages on,off,get and responds with on,off,unknown on the topic hotwater/status the status of the heater. The unknown message indicates that some unknown message was revieved.

The project consistes of a PI zero theat is attached to the hot water heater. Installed with py/HW_temps.py


- py/HW_status.py - Collects temps from the hotwater heater and publish them to the MQTT topic hotwater
- py/hw_ctrl.py - Controller script on the webserver PI that communicates with the hot water PI to control power 
- py/hw_device.py - Daemon script running on the hotwater PI to respond to power control requests from hw_ctrl.py 
- py/HW_temps.py - Main python script that collects the temperature data from HW_status.py and builds the heat map and does the calculations for energy content 
- py/Calibration.json
- py/part2
- www/HW_temps.php
- www/HW_status.php
- www/poweroff.png
- www/script.js
- www/gpio.php
- www/poweron.png
- www/favicon.ico
- www/blinkled.php



