/**
 * Code for the implementation of the speed sensors based on serial OBD device (in Raspberry Pi platform).
 * Created by Jesus Rodriguez, May 27, 2015.
 * Developed for DEPHISIT project.
 */

//-------------------- SpeedSensorBasedOnSerialOBD code --------------------//
var OBDReader = require('serial-obd');

var serialOBDReader;
var currentSpeed = 0; 

function SpeedSensorBasedOnSerialOBD(device, baudrate) {
    var options = {baudrate: baudrate};
    serialOBDReader = new OBDReader(device, options);

    serialOBDReader.on('dataReceived', function (data) {
        console.log(data);

        if (data.name === 'vss')
        {
            currentSpeed = data.value;
	    console.log("currentSpeed = %d", currentSpeed);
        }
    });

    serialOBDReader.on('connected', function () {
        console.log("Connected to OBD reader on %s (at %d Bd)", device, options.baudrate);

        this.addPoller("vss");

        this.startPolling(1000);
    });

    serialOBDReader.connect();
    console.log("Connecting to OBD reader...");
}

SpeedSensorBasedOnSerialOBD.prototype.getSpeed = function() {
    return currentSpeed;
}

module.exports = SpeedSensorBasedOnSerialOBD;
//--------------------------------------------------------------------------//
