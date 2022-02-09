#!/bin/bash 
# When the router rebbots on Sundays the network drops and we loose connectivity to the 
# the MQTT server.. so we just restart 
#
script="HW_temps2.py"
venvpath="/home/pi/hw-venv"
cd  ${venvpath}/Hotwater-tank-monitor 
if [ `ps -ef | grep $script| grep -v grep| wc -l| grep 0` ] ; then 
   logger "Collecting hotwater temperature ( ${script} )";
   source ${venvpath}/bin/activate
   python3 ${venvpath}/Hotwater-tank-monitor/py/${script} -m -v -d >> /tmp/hotwater.log 
fi

