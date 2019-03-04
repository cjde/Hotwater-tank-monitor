# Hotwater tank monitor

This is a hotwater tank monitoring applicaition. Attached to the A/C unit is a heat recovery unit. This provides hotwater through out the summer months. There is a Pi Zero that has 4 DS18B20 Digital temperature sensor (1 wire bus) that monitor the temperature of the tank at various points. These values are collected every minute and sent (via MQTT) to a PI "B" that is running MRTG ( and associated Web and DB ). The Pi"B" computes various energy components and the heat map of the tank. This goes into a very crude display ( mainly a PHP learning project ) to serve up to browsers.

The PI zero has reciently been equipped with at 12V SPDT relay attached to pin 26 ( with a 2N2222 ). This double pole relay is the power control to both phases of 240V main for the heating elements. The the python script hw_driver.py listens on the MQTT bus for the the topics hotwater/power with messages on,off,get and responds with on,off,unknown on the topic hotwater/status. The unknown message indicates that some unknown message was recieved. ( Perhaps the hw_driver.py scrip is not listening? )

These files are copied into the working working directory on PI B that is also running a webserver


- py/hw_ctrl.py - Controller script on the webserver PI that communicates with the hot water PI to control power via a MQTT message
- py/HW_status.py - Main python script that collects the temperature data via a MQTT message from HW_temps.py
- www/HW_status.php - PHP script that calls the HW_status.py to get the data from the hotwater pi and displays it
- www/script.js - implements that button callback for the power button
- www/gpio.php  - target of the javascript button push, calls the hw_ctrl.py to send the on off command to the MQTT topic hotwater/power
- www/poweroff.png - icon of the power button when off
- www/poweron.png - icon of the power button when on
- www/favicon.ico - icon for the webpage ocon



These files are installed on the Pi that is attached to the temperature sensors that are attached to the hotwater heater

- py/HW_temps.py - Cron scheduled script that updates MQTT hotwater topic with a json structure containing temps and metadata about the waterheater
```
  usage: HW_temps.py [-h] [--verbose] [--calibrate CALIBRATE] [--simulate]
                   [--test_calibration TEST_CALIBRATION] [--mqtt]

  Hotwater temp probe
  
  optional arguments:
    -h, --help            show this help message and exit
   --verbose, -v         verbose flag
   --calibrate CALIBRATE, -c CALIBRATE
                         Calculate calibration offsets. A value of 0 will load
                         the defaults
   --simulate, -s        simulate the device files instead of using the ones on
                         the PI
   --test_calibration TEST_CALIBRATION, -t TEST_CALIBRATION
                         Number or temp collections to run and apply the
                         calibration amount
   --mqtt, -m            Publish to MQTT server
```
- py/hw_device.py - Daemon script running on the hotwater PI to respond to power control requests from hw_ctrl.py
```It listens continously for the MQtt hotwater/power topic for these messages:

hotwater/power on     - the GPIO pin hat is controling the SSR of the hotwater heater is turned on
hotwater/power off    - the GPIO pin hat is controling the SSR of the hotwater heater is turned off
hotwater/status       - the current state of the hotwater SCR is returned
```
- py/Calibration.json - Calabration data for the temperature sensors In this example the top thermometer is needs 0.5 degrees to make it read the same as the others during the calabration run 
```
[
    0.5,
    0.0,
    0.0,
    0.0
]
```
- py/check_driver.sh - bash watchdog script to make sure that the HW driver is running ( run from cron ) 
- py/crontab - example crontab that publishes temperatures every minute ( via MQTT) and restartes the device driver if it exits and blinks the HB LED to signal that it is functioning corretly 
- blink2.py - script that is started by cron evey minute and blinks the green LED to signal that it is healthy.  

