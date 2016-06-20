<html>
<head>
	<title>Hot Water Tank Status and Control</title>
</head>
<body>

<?php 
echo "<pre>";
$json_str = shell_exec("/usr/bin/python /home/pi/hw_heater/HW_status.py -o hotwater.jpg" );
$json_obj = json_decode( $json_str );
echo "</pre>";
?>

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
			<td style="text-align: center;">
			<p>Power Status</p>

			<p><span style="color:#00FF00;">ON</span> <input checked="checked" name="power" type="radio" value="1" />
			   <span style="color:#FF0000;">OFF</span><input name="power" type="radio" value="0" /></p>
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
			<p style="text-align: center;">Water usage estimates</p>

			<p style="text-align: center;">&nbsp;</p>

			<table align="center" border="black" cellpadding="0" cellspacing="1" height="316" style="background-color: lightblue;" width="204">
				<tbody>
					<tr>
						<td style="border-color: black;">&nbsp;Temperature</td>
						<td style="border-color: black;">Duration (min)</td>
					</tr>
					<tr>
						<td style="border-color: black;">100</td>
						<td style="border-color: black">10</td>
					</tr>
					<tr>
						<td style="border-color: black;">90</td>
						<td style="border-color: black;">20</td>
					</tr>
					<tr>
						<td style="border-color: black;">80</td>
						<td style="border-color: black;">30</td>
					</tr>
					<tr>
						<td style="border-color: black;">70</td>
						<td style="border-color: black;">40</td>
					</tr>
				</tbody>
			</table>
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

