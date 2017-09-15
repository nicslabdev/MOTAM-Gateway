/**
 * NRF Communication code for manage the communication of the gateway (Raspberry Pi) with the wireless nodes (Arduino/Intel Galileo) through the RF24 interface.
 * Created by Jesus Rodriguez, May 27, 2015.
 * Developed for DEPHISIT project.
 */

const INVALID_HWDEVICEID				= 0x00
const INVALID_HWDEVICEACTION				= 0x00

const POSITION_SENSOR_TYPE  				= 0x01
const SPEED_SENSOR_TYPE  				= 0x02
const SEAT_SENSOR_TYPE  				= 0x03
const WEATHER_DETECTOR_TYPE  				= 0x04
const BICYCLE_DETECTOR_TYPE  				= 0x05
const TRAFFICLIGHT_DETECTOR_TYPE  			= 0x06
const DISPLAY_ACTUATOR_TYPE  				= 0x07
const LIGHT_ACTUATOR_TYPE    				= 0x08
const SOUND_ACTUATOR_TYPE    				= 0x09

const POSITION_SENSOR_GETPOSITION			= 0x01
const SPEED_SENSOR_GETSPEED				= 0x02
const SEAT_SENSOR_GETSEATSTATE				= 0x03
const WEATHER_DETECTOR_GETROADSTATE			= 0x04
const BICYCLE_DETECTOR_GETBICYCLESTATE			= 0x05
const TRAFFICLIGHT_DETECTOR_GETTRAFFICLIGHTSTATE	= 0x06
const DISPLAY_ACTUATOR_SETTEXTMESSAGE			= 0x07
const LIGHT_ACTUATOR_SETLIGHTON				= 0x08
const LIGHT_ACTUATOR_SETLIGHTOFF			= 0x09
const SOUND_ACTUATOR_PLAYSOUND				= 0x0A



// Require crypto library, and set key/iv buffers 
const crypto = require('crypto');
var key = new Buffer("6E552AA31014B4D55E1D05A6B6D8BBF5", "hex"); //Secret key generated randomly
var iv = new Buffer("", "hex");

var lastReceivedCounter = 0;
var lastSendedCounter = 0; 

// Secure message format:
//
//|  1 byte   |   1 byte   |      1 byte       |                    20 bytes                    | 1 byte  |                     8 bytes                    |
// --------------------------------------------------------------------------------------------------------------------------------------------------------
//| NrfNodeId | HwDeviceId | HwDeviceActionReq | HwDeviceActionReqData + Padding (random bytes) | Counter |  Reduced HMAC (First 8 bytes XOR Last 8 bytes) |
// --------------------------------------------------------------------------------------------------------------------------------------------------------

var generateRandomBytes = function(numberOfBytes) {
    
    //Generate and return random bytes
    //var randomBytes = crypto.pseudoRandomBytes(numberOfBytes);
    var randomBytes = crypto.randomBytes(numberOfBytes);

    console.log("randomBytes: " + randomBytes.toString("hex"));

    return randomBytes;
}

var generateReducedHmac = function(data) {

    //Calculate HMAC
    const hmac = crypto.createHmac('md5', key);
    hmac.update(data);
    var hmacData = hmac.digest();
    console.log("hmacData: " + hmacData.toString("hex"));

    //Generate reduced HMAC
    var reducedHmacData = new Buffer(8);
    for(var i = 0; i < reducedHmacData.length ; i++) {
	reducedHmacData[i] = hmacData[0+i] ^ hmacData[8+i];
    }
    console.log("reducedHmacData: " + reducedHmacData.toString("hex"));

    return reducedHmacData;
}

var requestMessageToSecureMessage = function(reqMessage) {

    var plainData = new Buffer(32);

    //Copy request message
    reqMessage.copy(plainData, 0, 0, Math.min(reqMessage.length, 23));

    //If needed, generate and add random bytes for padding
    if (reqMessage.length < 23) {
      var randomBytes = generateRandomBytes(23 - reqMessage.length);
      randomBytes.copy(plainData, reqMessage.length);
    }
  
    //Generate and add counter
    plainData[23] = ++lastSendedCounter;
  
    //Generate and add reduced HMAC
    var reducedHmac = generateReducedHmac(plainData.slice(0, 24));
    reducedHmac.copy(plainData, 24);
  
    console.log("requestMessageToSecureMessage - plainData: " + plainData.toString("hex"));

    //Encrypt the message to send using AES cipher in ECB mode (two blocks of 16 bytes).
    const cipher = crypto.createCipheriv('aes-128-ecb', key, iv);
    cipher.setAutoPadding(false);
    var secureMessage = cipher.update(plainData);
    cipher.final();

    console.log("requestMessageToSecureMessage - secureMessage: " + secureMessage.toString("hex"));

    //Return secure message generated
    return secureMessage;
}

var secureMessageToResponseMessage = function(secureMessage) {

    console.log("secureMessageToResponseMessage - secureMessage: " + secureMessage.toString("hex"));

    //Decrypt secure message
    const decipher = crypto.createDecipheriv('aes-128-ecb', key, iv);
    decipher.setAutoPadding(false);
    var plainData = decipher.update(secureMessage);
    decipher.final();

    console.log("secureMessageToResponseMessage - plainData: " + plainData.toString("hex"));

    //Generate reduced HMAC
    var reducedHmac = generateReducedHmac(plainData.slice(0, 24));

    //Check reduced HMAC. This verify both the data integrity and the authentication of a message.
    if (Buffer.compare(plainData.slice(24), reducedHmac) == 0) {

	//Get response message content
	var resMessage = plainData.slice(0, 23);
	console.log("resMessage: " + resMessage.toString("hex"));
		
	//Get received counter. Currently we do nothing with this counter.
	lastReceivedCounter = plainData[23];
	console.log("lastReceivedCounter: " + lastReceivedCounter);

	//Return response message
	return resMessage;
    } else {
	return null;
    }
}


// Sets the hub, once received the data, the rest of the module can be initialized -------------------------------
var setHub = function(h){
    hub = h;
    initialize();
};
exports.setHub = setHub;
// ---------------------------------------------------------------------------------------------------------------


// Initialize the module: define behaviour and open communication pipes ------------------------------------------
var initialize = function() {

    //TODO: Do this dinamically!!!
    var nrfDevices = [
	[
	    {hwDeviceType: DISPLAY_ACTUATOR_TYPE, ref: hub.nodes.intel_galileo.actuators.DA},
	    {hwDeviceType: LIGHT_ACTUATOR_TYPE, ref: hub.nodes.intel_galileo.actuators.LA},
	    {hwDeviceType: SOUND_ACTUATOR_TYPE, ref: hub.nodes.intel_galileo.actuators.SA}
	]
    ];


    //Define RX and TX variables
    var rx = null, tx = null;

    //Function for initialize NRF
    var radioInitialize = function () {

        tx = radio.openPipe('tx', 0xF0F0F0F0E1);
        rx = radio.openPipe('rx', 0xF0F0F0F0D2);
        //radio.printDetails();

        //Function for handle RX data
        rx.on('data', function (d) {
	    Array.prototype.reverse.call(d);

            console.log("Received " + d.length + " bytes. Content: " + d.toString('hex'));

	    if (d.length == 32) {

		//Decrypt and check the content received
		var resMessage = secureMessageToResponseMessage(d);
	    
		if (resMessage != null) {

		    //var nrfNodeId = d[0]-1;
		    //var hwDeviceId = d[1]-1;
		    //var hwDeviceActionRes = d[2];
		    var nrfNodeId = resMessage[0]-1;
		    var hwDeviceId = resMessage[1]-1;
		    var hwDeviceActionRes = resMessage[2];

		    /*if (hwDeviceId == INVALID_HWDEVICEID) {
		
		    }*/

		    switch (nrfDevices[nrfNodeId][hwDeviceId].hwDeviceType) {

		        case POSITION_SENSOR_TYPE:
			    switch (hwDeviceActionRes) {
		                case POSITION_SENSOR_GETPOSITION:
				    console.log("POSITION_SENSOR_GETPOSITION response");
				    break;
				default:
				    console.log("Unknown POSITION_SENSOR response");
				    break;
			    }
		            break;

			case SPEED_SENSOR_TYPE:
			    switch (hwDeviceActionRes) {
		                case SPEED_SENSOR_GETSPEED:
				    console.log("SPEED_SENSOR_GETSPEED response");
				    break;
				default:
				    console.log("Unknown SPEED_SENSOR response");
				    break;
			    }
		            break;

			case SEAT_SENSOR_TYPE:
			    switch (hwDeviceActionRes) {
		                case SEAT_SENSOR_GETSEATSTATE:
				    console.log("SEAT_SENSOR_GETSEATSTATE response");
				    break;
				default:
				    console.log("Unknown SEAT_SENSOR response");
				    break;
			    }
		            break;

			case WEATHER_DETECTOR_TYPE:
			    switch (hwDeviceActionRes) {
		                case WEATHER_DETECTOR_GETROADSTATE:
				    console.log("WEATHER_DETECTOR_GETROADSTATE response");
				    break;
				default:
				    console.log("Unknown WEATHER_DETECTOR response");
				    break;
			    }
		            break;

			case BICYCLE_DETECTOR_TYPE:
			    switch (hwDeviceActionRes) {
		                case BICYCLE_DETECTOR_GETBICYCLESTATE:
				    console.log("BICYCLE_DETECTOR_GETBICYCLESTATE response");
				    break;
				default:
				    console.log("Unknown BICYCLE_DETECTOR response");
				    break;
			    }
		            break;

			case TRAFFICLIGHT_DETECTOR_TYPE:
			    switch (hwDeviceActionRes) {
		                case TRAFFICLIGHT_DETECTOR_GETTRAFFICLIGHTSTATE:
				    console.log("TRAFFICLIGHT_DETECTOR_GETTRAFFICLIGHTSTATE response");
				    break;
				default:
				    console.log("Unknown TRAFFICLIGHT_DETECTOR response");
				    break;
			    }
		            break;

		        case DISPLAY_ACTUATOR_TYPE:
		            switch (hwDeviceActionRes) {
		                case DISPLAY_ACTUATOR_SETTEXTMESSAGE:
				    console.log("DISPLAY_ACTUATOR_SETTEXTMESSAGE response");

				    //TODO: Check response message correctly
				    if (nrfDevices[nrfNodeId][hwDeviceId].ref.DisplayValue.writeCallbackFunction != null) {
					nrfDevices[nrfNodeId][hwDeviceId].ref.DisplayValue.writeCallbackFunction(Characteristic.RESULT_SUCCESS);
					nrfDevices[nrfNodeId][hwDeviceId].ref.DisplayValue.writeCallbackFunction = null;
				    }
				    break;
				case INVALID_HWDEVICEACTION:
				    console.log("INVALID_HWDEVICEACTION response");

				    if (nrfDevices[nrfNodeId][hwDeviceId].ref.DisplayValue.writeCallbackFunction != null) {
					nrfDevices[nrfNodeId][hwDeviceId].ref.DisplayValue.writeCallbackFunction(Characteristic.RESULT_UNLIKELY_ERROR);
					nrfDevices[nrfNodeId][hwDeviceId].ref.DisplayValue.writeCallbackFunction = null;
				    }
				    break;
				default:
				    console.log("Unknown DISPLAY_ACTUATOR response");
				    break;
			    }
		            break;

			case LIGHT_ACTUATOR_TYPE:
		            switch (hwDeviceActionRes) {
		                case LIGHT_ACTUATOR_SETLIGHTON:
				    console.log("LIGHT_ACTUATOR_SETLIGHTON response");

				    //TODO: Check response message correctly
				    if (nrfDevices[nrfNodeId][hwDeviceId].ref.LightValue.writeCallbackFunction != null) {
					nrfDevices[nrfNodeId][hwDeviceId].ref.LightValue.writeCallbackFunction(Characteristic.RESULT_SUCCESS);
					nrfDevices[nrfNodeId][hwDeviceId].ref.LightValue.writeCallbackFunction = null;
				    }
				    break;
				case LIGHT_ACTUATOR_SETLIGHTOFF:
				    console.log("LIGHT_ACTUATOR_SETLIGHTOFF response");
	
				    //TODO: Check response message correctly
				    if (nrfDevices[nrfNodeId][hwDeviceId].ref.LightValue.writeCallbackFunction != null) {
					nrfDevices[nrfNodeId][hwDeviceId].ref.LightValue.writeCallbackFunction(Characteristic.RESULT_SUCCESS);
					nrfDevices[nrfNodeId][hwDeviceId].ref.LightValue.writeCallbackFunction = null;
				    }
				    break;
				case INVALID_HWDEVICEACTION:
				    console.log("INVALID_HWDEVICEACTION response");

				    if (nrfDevices[nrfNodeId][hwDeviceId].ref.LightValue.writeCallbackFunction != null) {
					nrfDevices[nrfNodeId][hwDeviceId].ref.LightValue.writeCallbackFunction(Characteristic.RESULT_UNLIKELY_ERROR);
					nrfDevices[nrfNodeId][hwDeviceId].ref.LightValue.writeCallbackFunction = null;
				    }
				    break;
				default:
				    console.log("Unknown LIGHT_ACTUATOR response");
				    break;
			    }
		            break;

			case SOUND_ACTUATOR_TYPE:
		            switch (hwDeviceActionRes) {
		                case SOUND_ACTUATOR_PLAYSOUND:
				    console.log("SOUND_ACTUATOR_PLAYSOUND response");

				    //TODO: Check response message correctly
				    if (nrfDevices[nrfNodeId][hwDeviceId].ref.SoundValue.writeCallbackFunction != null) {
					nrfDevices[nrfNodeId][hwDeviceId].ref.SoundValue.writeCallbackFunction(Characteristic.RESULT_SUCCESS);
					nrfDevices[nrfNodeId][hwDeviceId].ref.SoundValue.writeCallbackFunction = null;
				    }
				    break;
				case INVALID_HWDEVICEACTION:
				    console.log("INVALID_HWDEVICEACTION response");

				    if (nrfDevices[nrfNodeId][hwDeviceId].ref.SoundValue.writeCallbackFunction != null) {
					nrfDevices[nrfNodeId][hwDeviceId].ref.SoundValue.writeCallbackFunction(Characteristic.RESULT_UNLIKELY_ERROR);
					nrfDevices[nrfNodeId][hwDeviceId].ref.SoundValue.writeCallbackFunction = null;
				    }
				    break;
				default:
				    console.log("Unknown SOUND_ACTUATOR response");
				    break;
			    }
		            break;

		        default:
		            console.log("Unknown message profile.");
		    }

		} else {
		    console.log("Incorrect (reduced) HMAC.");
		}

	    } else {
		console.log("Incorrect message size.");
	    }
        });

	//Function for handle RX errors
    	rx.on('error', function (e) {
    	    console.warn("Error receiving rx.", e);
	    //Reinitiallizing the radio channel
	    radio.begin(radioInitialize);
    	});

    	//Function for handle TX errors
    	tx.on('error', function (e) {
    	    console.warn("Error sending tx.", e);
	    //Reinitiallizing the radio channel
	    radio.begin(radioInitialize);
    	});

    	/*rx.on('readable', function () {
    	    console.log('There is some data to read now.');
    	});

    	rx.on('end', function () {
            console.log('There will be no more data.');
    	});

    	rx.on('close', function () {
            console.log('Underlying resource has been closed.');
    	});

    	tx.on('finish', function() {
            console.log('All writes are now complete.');
    	});

    	tx.on('pipe', function(src) {
            console.log('Something is piping into the writer.');
    	});

    	tx.on('unpipe', function(src) {
            console.log('Something has stopped piping into the writer.');
    	});*/

	console.log('NRF24 communication channel configured.');
    };  

    //Initialize NRF communication
    console.log('NRF24 (nrf) module loading...');

    var nrf = require("nrf");

    console.log('NRF24 (nrf) module loaded.');


    console.log('Configuring NRF24 communication channel...');

    var radio = nrf.connect("/dev/spidev0.0", 24, 25);
    radio.channel(0x4c).transmitPower('PA_MAX').dataRate('250kbps').crcBytes(2).autoRetransmit({count: 15, delay: 4000});
    radio.begin(radioInitialize);


    //Functions for send action requests over NRF
    var sendSetTextMessageActionOverNRF24 = function(nrfNodeId, hwDeviceId, message) {
	//var textMessage = message.toString();
	//var textMessage = message.toString('ascii'); //-> río => rC-o
	/*var Iconv  = require('iconv').Iconv;
	var iconv = new Iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE');
	var textMessage = iconv.convert(message.toString()).toString(); //-> río => r'io*/
	var unidecode = require('unidecode');
	var textMessage = unidecode(message.toString()); //-> río => rio

	msg = new Buffer(3 + Math.min(textMessage.length + 1, 20));
	msg[0] = nrfNodeId;
	msg[1] = hwDeviceId;
	msg[2] = DISPLAY_ACTUATOR_SETTEXTMESSAGE;
	//msg.write(textMessage, 3, textMessage.length, 'utf8'); //-> Number of characters of the string
	//msg.write(textMessage, 3, Buffer.byteLength(textMessage)); //-> Number of bytes used by characters in this encoding
	msg.write(textMessage, 3, textMessage.length, 'ascii');
	if (msg < 20) { msg[msg.length-1] = null; }	

	//Encrypt request message
        var secureMessage = requestMessageToSecureMessage(msg);

	//console.log("Sending " + msg.length + " bytes. Content: " + msg.toString('hex'));
	//Array.prototype.reverse.call(msg);
	//tx.write(msg);
	console.log("Sending " + secureMessage.length + " bytes. Content: " + secureMessage.toString('hex'));
	Array.prototype.reverse.call(secureMessage);
	tx.write(secureMessage);
    }

    var sendSetLightOnOffActionOverNRF24 = function(nrfNodeId, hwDeviceId, on) {
	msg = new Buffer(3);
	msg[0] = nrfNodeId;
	msg[1] = hwDeviceId;
	if (on) {
	    msg[2] = LIGHT_ACTUATOR_SETLIGHTON;
	} else {
	    msg[2] = LIGHT_ACTUATOR_SETLIGHTOFF;
	}

	//Encrypt request message
        var secureMessage = requestMessageToSecureMessage(msg);

	//console.log("Sending " + msg.length + " bytes. Content: " + msg.toString('hex'));
	//Array.prototype.reverse.call(msg);
	//tx.write(msg);
	console.log("Sending " + secureMessage.length + " bytes. Content: " + secureMessage.toString('hex'));
	Array.prototype.reverse.call(secureMessage);
	tx.write(secureMessage);
    }

    var sendPlaySoundActionOverNRF24 = function(nrfNodeId, hwDeviceId) {
	msg = new Buffer(3);
	msg[0] = nrfNodeId;
	msg[1] = hwDeviceId;
	msg[2] = SOUND_ACTUATOR_PLAYSOUND;

	//Encrypt request message
        var secureMessage = requestMessageToSecureMessage(msg);

	//console.log("Sending " + msg.length + " bytes. Content: " + msg.toString('hex'));
	//Array.prototype.reverse.call(msg);
	//tx.write(msg);
	console.log("Sending " + secureMessage.length + " bytes. Content: " + secureMessage.toString('hex'));
	Array.prototype.reverse.call(secureMessage);
	tx.write(secureMessage);
    }

    //Set functions for send action requests over NRF
    for (i=0; i<nrfDevices.length; i++) {
	for (j=0; j<nrfDevices[i].length; j++) {
	    switch (nrfDevices[i][j].hwDeviceType) {
		case DISPLAY_ACTUATOR_TYPE:
		    nrfDevices[i][j].ref.DisplayValue.writeCallFunction = sendSetTextMessageActionOverNRF24;
		    break;
		case LIGHT_ACTUATOR_TYPE:
		    nrfDevices[i][j].ref.LightValue.writeCallFunction = sendSetLightOnOffActionOverNRF24;
		    break;
		case SOUND_ACTUATOR_TYPE:
		    nrfDevices[i][j].ref.SoundValue.writeCallFunction = sendPlaySoundActionOverNRF24;
		    break;
		default:
		    break;
	    }
	}
    }
};
// ---------------------------------------------------------------------------------------------------------------
