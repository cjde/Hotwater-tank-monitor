#!/bin/bash 
# When the router rebbots on Sundays the network drops and we loos connectivity to the 
# the MQTT server.. so we just restart 
# 
if [ `ps -ef | grep hw_device.py| grep -v grep| wc -l| grep 0` ] ; then 
   logger "Restarting hotwater heater device driver ( hw_device.py)"; 
   /usr/bin/python /home/pi/hw_heater/hw_device.py & 
fi

