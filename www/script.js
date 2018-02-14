//TheFreeElectron 2015, http://www.instructables.com/member/TheFreeElectron/
//JavaScript, uses pictures as buttons, sends and receives values to/from the Rpi
//These are all the buttons
// This javascript is run on the client browser behind hte powerbutton. 
// it calls the to tell the php script on the server 
// 
var button_0 = document.getElementById("button_0");

//This function is asking for gpio.php, receiving datas and updating the index.php pictures
function change_pin ( pic ) {
var data = 0;
//send the pic number to gpio.php for changes
//this is the http request
	var request = new XMLHttpRequest();
	request.open( "GET" , "gpio.php", true);
	request.send(null);
	//receiving informations
	request.onreadystatechange = function () {
		if (request.readyState == 4 && request.status == 200) {
			data = request.responseText;
			//update the index pic
			if ( !(data.localeCompare("0\n")) ){
			        button_0.src = "poweroff.png";
				// alert ("off" );
			}
			else if ( !(data.localeCompare("1\n")) ) {
				 button_0.src = "poweron.png";
				// alert ("on" );
			}
			else if ( !(data.localeCompare("2\n"))) {
				alert ("Something went wrong! not 0 or 1 " );
				return ("fail");			
			}
                        else if ( !(data.localeCompare("-1\n"))) {
                                alert ("No responce from HW heater driver " );
                                return ("fail");
                        }
			else {
				alert ("Something else went wrong!" );
				return ("fail"); 
			}
		}
		//test if fail
		else if (request.readyState == 4 && request.status == 500) {
			alert ("server error");
			return ("fail");
		}
		//else 
		else if (request.readyState == 4 && request.status != 200 && request.status != 500 ) { 
			alert ("Something went wrong!");
			return ("fail"); }
	}	
	
return 0;
}
