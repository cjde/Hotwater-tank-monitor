# Hotwater tank monitor

This is a hotwater tank monitoring applicaition. Attached to the A/C unit is a heat recovery unit. This provides hotwater through out the summer months. There is a Pi Zero that has 4 DS18B20 Digital temperature sensor (1 wire bus) that monitor the temperature of the tank at various points. These values are collected every minute and sent (via MQTT) Home Assistant 

The PI zero has reciently been equipped with at 12V SPDT relay attached to pin 26 ( with a 2N2222 ). This double pole relay is the power control to both phases of 240V main for the heating elements. The the python script hw_driver2.py listens on the MQTT bus for the the topics hotwater-v2/power with messages ON,OFF,GET and responds with the ON OFF on the topic hotwater-v2/status. 

The two python scripts are run from inside a venv and the git clone is to a directory in that venv directory. To install this follow these steps

```
cd /home/pi/hw-venv
source bin/activate
git clone  git+ssh://git@github.com/cjde/Hotwater-tank-monitor.git
cd Hotwater-tank-monitor/
python3 -m pip install -r requirements.txt
sudo apt-get install mosquitto-clients
```
Edit the config file and fill in the details for your network

```
# Broker details
MQTTbroker = "homeassistant.hm"
User = "mqttuser"
Password = "mqttpass"
PORT = 1883

# Tank details
TANKSIZE = 50.0
# temperature of the water flowing into the tank ( in degrees F )
ROOM_TEMP=74.0

# Script details
# location of the directory that contains links to the devices or
# directories of files that represent the simulated driver files
HOMEDIR = "/home/pi/hw-venv/Hotwater-tank-monitor"
# This is the distance from the top of the tank to the probe location ( in 10ths of an inch)
PROBE_DIST_LIST=[0, 170, 410, 530]
```

The file  for the probes are in Calibration.json. These values are in degrees celcius. In this example the top thermometer needs 0.5 degrees to make it read the same as the others when the tank has reached equilibrium. This will most likely need to be adjusted for your set of DS18B20 
```
[
    0.5,
    0.0,
    0.0,
    0.0
]

```

You should nowbe able to test it. 
- Verify that mosquito is installed and you cant talt to the MQTT broker 
```
mosquitto_pub -h homeassistant.hm -t hotwater-v2/power -m OFF -u mqttuser -P mqttpass -i cron.$$
```
- Verify that you can send and recieve messages
```
mosquitto_sub -h homeassistant.hm -t hotwater-v2/status  -u mqttuser -P mqttpass -i cron.$$ & 
mosquitto_pub -h homeassistant.hm -t hotwater-v2/power -m GET -u mqttuser -P mqttpass -i cron.$$ 
```
- Send a message to turn it on and off and you should get a responce from the mosquitto_pub that was statted in background earlier. AFter the test kill the mosquito_pub program 

```
bash sh/turnon.sh
bash sh/turnoff.sh 
kill %1 

```

- Verify that the heartbeat blinking LED works to indicate that the PI is heathy 

```
python /home/pi/hw-venv/Hotwater-tank-monitor/py/blink2.py
```

- Verify that you can read the calibration file, the simulated I2C sensors and publish to Home assistant. Then run it again this time not simulating the devices but instead use the real device files that are linked to from the sensors directory. This directory will need to have links that point to the devices for your PI

```
python3 /home/pi/hw-venv/Hotwater-tank-monitor/py/HW_temps2.py -m -v -d -s
python3 /home/pi/hw-venv/Hotwater-tank-monitor/py/HW_temps2.py -m -v -d 
```

- Verify that the service that turns on and off the relay is operational. Start up the power listner then send a MQTT message to it. Kill the hw_device2.py script when succesfull

```
python3 /home/pi/hw-venv/Hotwater-tank-monitor/py/hw_device2.py -d  & 
bash sh/turnon.sh
bash sh/turnoff.sh 
kill %1 
```

- It should all be working add them to cron to watchdog the power control script and to start the sensor collector every minute. The default crontab also turns the heater on and off at 4:30pm and 7:30pm. After a minute check to see that the blink2.py the hw_device2.py are running and the hw_temps2.py is running every minute

```
crontab crontab  
ps -ef | grep python 
```

Once it is all operational you can add the config file HomeAssist/HASIO_configuration.yml to the to homeassistant in configuration.yml file. 
Test the config file 
- in he lovelace UI got to Configuration->Server Controls->Configuration Check Configuration
Once that passes 
- goto Supervisor->System->Core and Restart Core 
- then Configuration->Integrations->Mosquito Broker->Configure. Start listening to the hotwater-v2/power topic 
In the Lovelace UI 
- add a new "Vertical Stack Card Configuration"
- click on show code editor 
- paste in the contents of HomeAssist/lovelaceHotwaterconfig

TADA! 
You should now have the on/off button atthe top along with guage and a graph of the sensors 



### Hotwater temp probe
```
usage:hw_temps2.py [-h] [--verbose] [--calibrate CALIBRATE] [--simulate]
                    [--test_calibration TEST_CALIBRATION] [--debug] [--mqtt]
                    [--broker BROKER] [--user USER] [--password PASSWORD]
                    [--home HOME]


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
  --debug, -d           Enable Debug output.
  --mqtt, -m            Publish to MQTT server
  --broker BROKER, -o BROKER
                        IP or name of MQTT broker
  --user USER, -u USER  Username for QQTT broker
  --password PASSWORD, -p PASSWORD
                        Password for MQTT broker
  --home HOME, -H HOME  Base directory for the sensors
```

### Hotwater MQTT device driver
```
usage: hw_device2.py [-h] [--broker BROKER] [--user USER]
                     [--password PASSWORD] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --broker BROKER, -o BROKER
                        IP or name of MQTT broker
  --user USER, -u USER  Username for MQTT broker
  --password PASSWORD, -p PASSWORD
                        Password for MQTT broker
  --debug, -d           Enable Debug output.

```


NOTE: The www and py/OLD directories are old and no longer used. 

