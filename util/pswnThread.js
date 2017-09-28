/**
 * Execution thread for position sensors deployed on Raspberry Pi platform.
 * Created by Jesus Rodriguez, May 27, 2015.
 * Modified by Manuel Montenegro, Sept 19, 2017.
 * Developed for MOTAM project.
 */

var util = require('util');

// Received device path from parent thread (node.js)
var devicePath = process.argv[2];

var PositionSensorBasedOnGPSD = require('./PositionSensorBasedOnGPSD');

// GPS is initialized in devicePath
var positionSensor = new PositionSensorBasedOnGPSD('/usr/sbin/gpsd', devicePath, 2947);

console.log('pswnThread started. GPS on ' + devicePath);

setInterval(function() {
	pswnPosition = positionSensor.getPosition();
	// console.log('pswnThread >> POSITION ' + util.inspect(pswnPosition, false, null));
	process.send(pswnPosition);	
}, 1000);