/**
 * Execution thread for speed sensors deployed on Raspberry Pi platform.
 * Created by Jesus Rodriguez, May 27, 2015.
 * Developed for DEPHISIT project.
 */

var util = require('util');

var SpeedSensorBasedOnSerialOBD = require('./SpeedSensorBasedOnSerialOBD');

var speedSensor = new SpeedSensorBasedOnSerialOBD('/dev/pts/3', 38400);

console.log('sswnThread started');

setInterval(function() {
  sswnPosition = speedSensor.getSpeed();
  console.log('sswnThread >> SPEED ' + util.inspect(sswnPosition, false, null));
  process.send(sswnPosition);
}, 1000);

