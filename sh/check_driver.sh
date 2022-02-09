#!/bin/bash 
# When the router rebbots on Sundays the network drops and we loos connectivity to the 
# the MQTT server.. so we just restart 
#
venvpath="/home/pi/hw-venv"
if [ `ps -ef | grep hw_device2.py| grep -v grep| wc -l| grep 0` ] ; then 
   logger "Restarting hotwater heater device driver V2( hw_device2.py)";
   source ${venvpath}/bin/activate
   python3 ${venvpath}Hotwater-tank-monitor/py/hw_device2.py &
fi

