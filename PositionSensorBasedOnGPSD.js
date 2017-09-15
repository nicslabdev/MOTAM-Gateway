/**
 * Code for the implementation of the position sensors based on "gpsd" daemon (in Raspberry Pi platform).
 * Created by Jesus Rodriguez, May 27, 2015.
 * Developed for DEPHISIT project.
 */

//-------------------- PositionSensorBasedOnGPSD code --------------------//
var gpsd = require('node-gpsd');

var currentLatitude = 0.0;
var currentLongitude = 0.0;

function PositionSensorBasedOnGPSD(program, device, port) {

    var daemon = new gpsd.Daemon({
	port: port,
        program: program,
        device: device
    });

    daemon.start(function() {
        var listener = new gpsd.Listener({port: port});
    
        listener.on('TPV', function (tpv) {
	    //console.log(tpv);

	    if (tpv.mode === 2 || tpv.mode === 3) {
	        currentLatitude = tpv.lat;
	        currentLongitude = tpv.lon;
	    }
        });
    
        listener.connect(function() {
            listener.watch();
        });
    });
}

PositionSensorBasedOnGPSD.prototype.getPosition = function() {
    return {latitude: currentLatitude, longitude: currentLongitude};
}

module.exports = PositionSensorBasedOnGPSD;
//------------------------------------------------------------------------//
