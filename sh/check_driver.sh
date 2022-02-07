#!/bin/bash 
# When the router rebbots on Sundays the network drops and we loos connectivity to the 
# the MQTT server.. so we just restart 
# 
if [ `ps -ef | grep hw_device2.py| grep -v grep| wc -l| grep 0` ] ; then 
   logger "Restarting hotwater heater device driver V2( hw_device2.py)"; 
   /usr/bin/python3 /home/pi/hw_heater/repo/py/hw_device2.py & 
fi

