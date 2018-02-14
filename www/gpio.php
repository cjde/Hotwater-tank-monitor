<?php
// This PHP script calls the python script that puts messages on the MQTT message bus 
// to communicate to the HW heater pi that is somewhewre else in the network. If the 
// status of the heater is 0 (off ) then another message is sent to it ti turn it off
// Return: 
//   0 the power was turned off  
//   1 the the power was turned on  
//  -1 the hotwater heater driver did not return a status ( maybe it is off ?)
//
//   If there are errors then descriptive text string is also output 
//
// TODO: 
//    An attitional option -t could be implemented to just tel the hotwater heater to 
//    toggle its state and report back what it changed it to. This would allow a 
//    quicker turn around and would only incure one MQTT message

//reading pin's status
exec ("/usr/bin/python /var/www/ceeberry/onebut/hw_ctrl.py -g", $output, $rt );
$st = end( $output); 
// echo "get status is ",$st; 

if ($st == "1" ) {
   // if on turn it off 
   exec ("/usr/bin/python /var/www/ceeberry/onebut/hw_ctrl.py -f", $output, $rt );
   $st = end( $output);
   // echo "was on, now:",$st; 
   //print_r ( $output);
}
else if ($st == "0" ) {
   // if off turn it on 
   exec ("/usr/bin/python /var/www/ceeberry/onebut/hw_ctrl.py -n", $output, $rt );
   $st = end( $output);
   // echo "was off, now:",$st; 
   //print_r ( $output);
}
else if ($st == "-1" ) {
   // look like the MQTT server is not up? 
   echo "Hotwater tank  driver not responding: "; 
   //print_r ( $output);
}
else  {
   // hmmm.... somethin wrong in python land ! 
   echo "Bad return code from /usr/bin/python hw_ctrl.py ";
   print_r ( $output);
}


//output the status code as the last line
# echo "stat: ",$st;
echo $st;
?>

