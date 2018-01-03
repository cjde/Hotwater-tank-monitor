<html>
<head>
<title>Hot Water Tank Status and Control</title>
<link rel="icon" href="http://192.168.2.15/hw/favicon.ico" />
<link rel=”icon” sizes=”192×192″ href=”http://192.168.2.15/hw/favicon.png”>
<link rel=”icon” sizes=”128×128″ href=”http://192.168.2.15/hw/favicon.png”>
</head>
<body>

<?php 
echo "<pre>";
$json_str = shell_exec("/usr/bin/python /home/pi/hw_heater/HW_status.py -o hotwater.jpg" );
$json_obj = json_decode( $json_str );
$gooo=111;
echo "</pre>";
?>

<script type="text/javascript" src="http://www.google.com/jsapi"></script>
<script type="text/javascript">
    google.load('visualization', '1', {packages: ['gauge']});
</script>

<script type="text/javascript">
   function drawVisualization() {
   // Create and populate the data table.
   // get ithe new json element and add them to th guages here 
      var data = google.visualization.arrayToDataTable(
      [
        ['Label', 'Value'],
        ['Input', <?php  echo 78 ?> ],
        ['From Exch',  <?php  echo round( $json_obj->temp_listf[0]) ?>],
        ['To Exch',  <?php  echo round( $json_obj->temp_listf[3]) ?> ]
      ]
      );

      var options = {
        min: 60, max: 140,
        greenFrom: 60, greenTo: 84,
        redFrom: 116, redTo: 140,
        minorTicks: 10
      };

     // Create and draw the visualization.
     new google.visualization.Gauge(document.getElementById('visualization')).
     draw(data, options);
}

google.setOnLoadCallback(drawVisualization);
</script>


<p>&nbsp;</p>


<table border="black" cellpadding="0" cellspacing="0" height="681" width="623" border-radius="50px">
<tbody>
	<tr>
		<td colspan="3">
		<h2 style="text-align: center;">Hot Water Tank Control</h2>
		<?php
		echo "<center>";
		echo date("M d Y h:i:s A") . "<br>";
		echo "</center>"
		?>

	</tr>
	<tr>
		<td>
		<p style="text-align: center;">Heat map</p>
		</td>
		<td style="text-align: center;"> Power  

        <?php
        // this realy only needs to be a scalar , not anarray
        $val_array = array(0,0,0,0,0,0,0,0);
        $Pins = array( 5,6,10,11,5,6,10,11 );

        // what is the ordinal value of the pin in the array ?
        $i =0;
        $pin = $Pins[$i];

        //set the intial state on the pin and set it the indicator to that
        system("gpio mode ".$pin." out");
        exec ("gpio read ".$pin, $val_array[$i], $return );

        //if gpio is  off
        if ($val_array[$i][0] == 1 ) {
                echo ("<img id='button_0' src='poweron.png' height='65' width='65' align=middle onclick='change_pin (".$i.");'/>");
        }
        //if f gpio is on
        if ($val_array[$i][0] == 0 ) {
                echo ("<img id='button_0' src='poweroff.png' height='65' width='65' align=middle onclick='change_pin (".$i.");'/>");
        }
        ?>
        <!-- javascript -->
        <script src="script.js"></script>



		</td>
		<td style="text-align: center; border-color: black;">
		<p>Energy Content</p>

		<p><strong>
		<?php 
			echo $json_obj->BTU, " BTU"
                        ?>
			</strong></p>
			</td>
		</tr>
		<tr>
			<td rowspan="4"><br />
			<img alt="Temp map" src="hotwater.jpg" style="display: block; margin-left: 20; margin-right: 20; " /></td>
			<td rowspan="4" style="text-align: center;">
			<p style="text-align: center;">Heat Recovery</p>

 <div id="visualization" style="width: 200px; height: 575px;"></div> 

			<p style="text-align: center;">&nbsp;</p>

			</td>
			<td style="text-align: center; white-space: nowrap; vertical-align: middle;">
			<p style="text-align: center;"><strong>Peter Trigger</strong></p>

			<p>Set Temp: <input maxlength="3" name="temp1" size="5" type="text" value="100" /></p>
			<p>&nbsp<span style="color:#00FF00;">Enable</span><input name="trigger1" type="radio" value="on" /> 
			<span style="color:#FF0000;">Disable</span><input checked="checked" name="trigger1" type="radio" value="off" />
			</p>
			</td>
		</tr>
		<tr>
			<td style="text-align: center; white-space: nowrap; vertical-align: middle;">
			<p style="text-align: center;"><strong>Theresa Trigger</strong></p>

			<p>Set Temp: <input maxlength="3" name="temp2" size="5" type="text" value="100" /></p>
			<p>&nbsp<span style="color:#00FF00;">Enable</span><input name="trigger2" type="radio" value="on" /> 
			<span style="color:#FF0000;">Disable</span><input checked="checked" name="trigger2" type="radio" value="off" />
			</p>
			</td>
		</tr>
		<tr>
			<td style="text-align: center; white-space: nowrap; vertical-align: middle;">
			<p style="text-align: center;"><strong>Jeanne Trigger</strong></p>

			<p>Set Temp: <input maxlength="3" name="temp3" size="5" type="text" value="100" /></p>
			<p>&nbsp<span style="color:#00FF00;">Enable</span><input name="trigger3" type="radio" value="on" /> 
			<span style="color:#FF0000;">Disable</span><input checked="checked" name="trigger3" type="radio" value="off" />
			</p>
			</td>
		</tr>
		<tr>
			<td style="text-align: center; white-space: nowrap; vertical-align: middle;">
			<p style="text-align: center;"><strong>Chris Trigger </strong></p>

			<p>Set Temp: <input maxlength="3" name="temp4" size="5" type="text" value="100" /></p>
			<p>&nbsp<span style="color:#00FF00;">Enable</span><input name="trigger4" type="radio" value="on" /> 
			<span style="color:#FF0000;">Disable</span><input checked="checked" name="trigger4" type="radio" value="off" />
			</p>
			</td>			
		</tr>
		<tr style="text-align: center;">
<td colspan="3";style="text-align: center;" >
<DIV><B>24 hour Hotwater tank energy content</B></DIV>
<DIV><A HREF="../../mrtg/hw.html"><IMG BORDER=1 ALT="hw Traffic Graph" SRC="../../mrtg/hw-day.png" width="625"></A><BR>
<SMALL><!--#flastmod file="../../mrtg/hw.html" --></SMALL></DIV>
</td><td></td>
		</tr>

	</tbody>
</table>
</body>
</html>

