/**
 * Execution thread for position sensors deployed on Raspberry Pi platform.
 * Created by Jesus Rodriguez, May 27, 2015.
 * Modified by Manuel Montenegro, Sept 15, 2017.
 * Developed for MOTAM project.
 */

var util = require('util');

var PositionSensorBasedOnGPSD = require('./PositionSensorBasedOnGPSD');

//Use a different port than the default (needed in Debian 8) ---------------------------------------
var positionSensor = new PositionSensorBasedOnGPSD('/usr/sbin/gpsd', '/dev/ttyUSB0', 2947);
//--------------------------------------------------------------------------------------------------

console.log('pswnThread started');

setInterval(function() {
  pswnPosition = positionSensor.getPosition();
  console.log('pswnThread >> POSITION ' + util.inspect(pswnPosition, false, null));
  process.send(pswnPosition);	
}, 1000);

