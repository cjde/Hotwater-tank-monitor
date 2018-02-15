<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>Raspberry Pi Gpio</title>
    </head>

    <body style="background-color: ;">
        <?php

// This is a demonstration script used to test the functionality of the interface to the MQTT message bus 
//
// This PHP file is run on the server. It gets the current state of the hotwater heater power and then 
// sets up a button that changes state each time it is pressed. When it it pressed it it toggles the power 
// on to off or off to on 
//   

        $val_array = array();

        // what is the ordinal value of hte pin in the array ?
        $i =0;

        //get  then initial state of the hot waterheater and set it the indicator to that 
        exec ("/usr/bin/python /var/www/ceeberry/onebut/hw_ctrl.py -g ", $val_array[$i], $return );
        echo ("Initilizing, get status is :");
        $st = end($val_array[$i]);
        echo $st ."<br>"; 
        print_r ($val_array[$i]);

        //if gpio is on then set the initial button to on  
        if ($st == 1 ) {
                echo ("<img id='button_0' src='poweron.png' height='32' width='32' onclick='change_pin (0);'/>");
        }
        //if gpio is off then set the initial button to off 
        if ($st == 0 ) {
                echo ("<img id='button_0' src='poweroff.png' height='32' width='32' onclick='change_pin (0);'/>");
        }
        ?>

        <!-- javascript -->
        <script src="script.js"></script>
    </body>
</html>

