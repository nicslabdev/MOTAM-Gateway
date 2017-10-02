/**
 * Main code for create BLE peripheral devices of the MOTAM platform.
 * Created by Jesus Rodriguez, May 27, 2015.
 * Modified by Manuel Montenegro, Oct 2, 2017.
 * Developed for MOTAM project.
 */

var SerialPort = require("serialport");
var util = require('util');
var execSync = require('child_process').execSync;
var bleno = require('bleno');
var fork = require('child_process').fork;
var spawn = require('child_process').spawn;
var dialog = require('dialog');

// Opening serial port for Arduino
var port = new SerialPort("/dev/ttyACM0",{
  baudRate: 9600
});

//Kill all instances of bluetoothd (needed to work bleno with BlueZ >= 5.17) --------------------------
// console.log("Getting BlueZ version...");
var bluezVersion = parseFloat(execSync("bluetoothd -v"));
// console.log("BlueZ version: " + bluezVersion);
if (bluezVersion >= 5.17) {
    // console.log("Killing all instances of bluetoothd (needed to work bleno with BlueZ >= 5.17...");
    if (execSync("ps aux").indexOf("bluetoothd")>=0) {
        execSync("killall bluetoothd");
    }    
    execSync("hciconfig hci0 up");
}
// ----------------------------------------------------------------------------------------------------

var BlenoPrimaryService = bleno.PrimaryService;
var BlenoCharacteristic = bleno.Characteristic;
var BlenoDescriptor = bleno.Descriptor;

//De la plataforma Arduino va a llegar lo siguiente:
//  TSWN:50:IndoorTemperature - TemperatureValue
//  TSWN:50:IndoorTemperature - TemperatureThreshold
//que se habra generado a partir de TSWN(pin11, 30, 5, 0)


//TODO: Do this dinamically!!!
// Define the configuration and properties of the gateway. This definition will be properly used by the modules
// to create the interfaces and services.
var hub = {
    ble: { 
        name: 'DephisitGateway',
	uuid: '0000'
    },
    nodes: {
        rpi: {
            sensors: {
		PSWN: {
                       PositionValue: {
			    uuid: '0001',
                            descriptorValue: 'PSWN:50:VehiclePosition',

			    readCallFunction: null,
			    readCallbackFunction: null,
			    readCallbackResult: undefined,

			    enableNotificationCallFunction: null,
			    disableNotificationCallFunction: null,

			    onChangeValueCallback: null
                        },
                        PositionThreshold: {
			    uuid: '0002',
                            descriptorValue: 'PSWN:50:VehiclePosition',

			    writeCallFunction: null
                        }
                },
		SSWN: {
                       SpeedValue: {
			    uuid: '0003',
                            descriptorValue: 'SSWN:50:VehicleSpeed',

			    readCallFunction: null,
			    readCallbackFunction: null,
			    readCallbackResult: undefined,

			    enableNotificationCallFunction: null,
			    disableNotificationCallFunction: null,

			    onChangeValueCallback: null
                        },
                        SpeedThreshold: {
			    uuid: '0004',
                            descriptorValue: 'SSWN:50:VehicleSpeed',

			    writeCallFunction: null
                        }
                }
            },
            actuators: {
            }
        },
	intel_galileo: {
	    sensors: {
            },
            actuators: {
		DA: {
                       DisplayValue: {
			    uuid: '0006',
                            descriptorValue: 'DA:50:WarningDisplayActuator',

			    writeCallFunction: null,
			    writeCallbackFunction: null
                        },
			NrfInfo: {
			    nrfNodeId: 1,
			    hwDeviceId: 1
			}
                },
		LA: {
                       LightValue: {
			    uuid: '0007',
                            descriptorValue: 'LA:50:WarningLightActuator',

			    writeCallFunction: null,
			    writeCallbackFunction: null
                        },
			NrfInfo: {
			    nrfNodeId: 1,
			    hwDeviceId: 2
			}
                },
		SA: {
                       SoundValue: {
			    uuid: '0008',
                            descriptorValue: 'SA:50:WarningSoundActuator',

			    writeCallFunction: null,
			    writeCallbackFunction: null
                        },
			NrfInfo: {
			    nrfNodeId: 1,
			    hwDeviceId: 3
			}
                }, 
	    }
	}
    }
};

console.log('Creating BLE peripheral...');

// ---------------------- USB devices discovery -------------------------- //

// Execute usbDiscovery shell script that
// list usb devices currently connected
// usbDevices is an string which contains an ID and a path of usb devices

var usbDevices = execSync("/home/pi/MOTAM/util/usbDiscovery");

// separate each line (each device) in array elements
var arrayUsbDevices = usbDevices.toString().split("\n");

var gpsDevicePath;
var obd2DevicePath;

console.log('------------- Connected devices list ----------------');
for (line of arrayUsbDevices) {
    // if ID_MODEL_ID = 2303: GPS GlobalSat BU-353S54
    if(line.substr(0,4) == 2303) {
        gpsDevicePath = line.substr(5);
        console.log('GPS detected on '+gpsDevicePath);

    // if ID_MODEL_ID = 7523: OBD2 ELM327 interface
    } else if(line.substr(0,4) == 7523) {
        obd2DevicePath = line.substr(5);
        console.log('OBD2 interface detected on '+obd2DevicePath);
    }
}
console.log('-----------------------------------------------------');



// ----------------------------- SSWN Thread ----------------------------- //

var sswnNotifyCallback;
var sswnThreshold = 0;
var sswnCurrentSpeed = 0;

// if not connected a OBD2 interface device
if (!obd2DevicePath) {
    // execute an GUI dialog. If you press YES, it will run the OBD2 interface simulator.
    // zenity show in shell a warning message, so stdin and stderr is ignored.
    // zenity returns '0' for yes and '1' for no
    var runSim = execSync("/home/pi/MOTAM/util/zenity",{stdio:['ignore','pipe','ignore']});
    
    // if the choice has been "yes"
    if (runSim==0) {
        // kill previous obdsim processes
        if (execSync("ps aux").indexOf("obdsim")>=0) {
            execSync("killall obdsim");
        }

// SOCAT
        // spawn('socat', ['-d', '-d', 'pty,raw,echo=0,link=/tmp/ttyV0', 'pty,raw,echo=0,link=/tmp/ttyV1']);

        // run obdsim with GUI
        var obdsim = spawn('obdsim', ['-g', 'gui_fltk', '-t', '/dev/tty50']);

        obd2DevicePath = '/dev/tty50';

    }
} 


// if there is a connected obd interface or running obd sim..
if (obd2DevicePath) {
	console.log("OBD2 PORT: "+obd2DevicePath);
	// Initialize sswnThread.py python script
	var spawn = require('child_process').spawn,
	    py    = spawn('python', ['/home/pi/MOTAM/util/sswnThread.py']),
	    data = obd2DevicePath;
	// When python script send some data to node, this is saved in "data"
	py.stdout.on('data', function(data) {
	    // Receive speed from pyOBD_node.py python Script
	    sswnNewSpeed = parseInt(data,10);
	    if (sswnNotifyCallback != null && Math.abs(sswnNewSpeed - sswnCurrentSpeed) > sswnThreshold) {
	        var dataBLE = new Buffer(4);
	        dataBLE.writeInt32LE(sswnNewSpeed, 0);
	        sswnNotifyCallback(dataBLE);
	    }
	    console.log('OBD2-Speed: ' + sswnNewSpeed);
	    sswnCurrentSpeed = sswnNewSpeed;
	});

	// Write obd2DevicePath from this thread to sswnThread.py
	py.stdin.write(JSON.stringify(data));
	py.stdin.end();
}


// ----------------------------- Speed Value Characteristic ----------------------------- //

var SpeedValueCharacteristic = function () {
SpeedValueCharacteristic.super_.call(this, {
    uuid: hub.nodes.rpi.sensors.SSWN.SpeedValue.uuid,
    properties: ['read','notify'],
    descriptors: [
        new BlenoDescriptor({
            uuid: '2901',
            value: hub.nodes.rpi.sensors.SSWN.SpeedValue.descriptorValue
        })
    ],
    onReadRequest: function (offset, callback) {
    console.log('SpeedValueCharacteristic onReadRequest - offset=' + offset + ' ,callback=' + callback);

    var data = new Buffer(4);
    data.writeInt32LE(sswnCurrentSpeed, 0);
        callback(this.RESULT_SUCCESS, data);
    },
    onSubscribe: function(maxValueSize, updateValueCallback) { 
    console.log('SpeedValueCharacteristic onSubscribe - maxValueSize=' + maxValueSize + ' ,updateValueCallback=' + updateValueCallback);

    sswnNotifyCallback = updateValueCallback;
    },
    onUnsubscribe: function() {
        console.log('SpeedValueCharacteristic onUnsubscribe');

    sswnNotifyCallback = null;
    },
    onNotify: function() {
    console.log('SpeedValueCharacteristic onNotify');
    }
});
};

util.inherits(SpeedValueCharacteristic, BlenoCharacteristic);


// ----------------------------- Speed Threshold Characteristic ----------------------------- //

var SpeedThresholdCharacteristic = function () {
SpeedThresholdCharacteristic.super_.call(this, {
    uuid: hub.nodes.rpi.sensors.SSWN.SpeedThreshold.uuid,
    properties: ['write', 'writeWithoutResponse'],
    descriptors: [
        new BlenoDescriptor({
            uuid: '2901',
            value: hub.nodes.rpi.sensors.SSWN.SpeedThreshold.descriptorValue
        })
    ],
    onWriteRequest: function (data, offset, withoutResponse, callback) {

        console.log('SpeedThresholdCharacteristic onWriteRequest - data=' + data.toString('hex') + ', offset=' + offset + ', withoutResponse=' + withoutResponse + ', callback=' + callback);
    
    //TODO Change to readInt16LE()???
    sswnThreshold = data.readInt32LE(0);
    console.log('sswnThreshold: ' + sswnThreshold);

    callback(this.RESULT_SUCCESS);
    }
});
};

util.inherits(SpeedThresholdCharacteristic, BlenoCharacteristic);



// ----------------------------- PSWN Thread ----------------------------- //

var pswnNotifyCallback;

var pswnCurrentPos = {latitude: 0, longitude: 0};
var pswnThreshold = 0;

// Check if exist a connected GPS Device
if (!gpsDevicePath) {
    console.log('GPS device not detected')
} else {
    // Care! Argument of child process is passed between []
    var pswnThread = fork('/home/pi/MOTAM/util/pswnThread.js', [gpsDevicePath]);

    pswnThread.on('message', function(pswnNewPos) {
        if (pswnNotifyCallback != null && Math.max(Math.abs(pswnNewPos.latitude - pswnCurrentPos.latitude), Math.abs(pswnNewPos.longitude - pswnCurrentPos.longitude)) > pswnThreshold) {
            var data = new Buffer(8);
            data.writeFloatLE(pswnNewPos.latitude, 0);
            data.writeFloatLE(pswnNewPos.longitude, 4);
            pswnNotifyCallback(data);
        }
        pswnCurrentPos = pswnNewPos;
        console.log('POSITION ' + util.inspect(pswnCurrentPos, false, null));
    });
}

// ----------------------------- Position Value Characteristic ----------------------------- //

var PositionValueCharacteristic = function () {
PositionValueCharacteristic.super_.call(this, {
    uuid: hub.nodes.rpi.sensors.PSWN.PositionValue.uuid,
    properties: ['read','notify'],
    descriptors: [
        new BlenoDescriptor({
            uuid: '2901',
            value: hub.nodes.rpi.sensors.PSWN.PositionValue.descriptorValue
        })
    ],
    onReadRequest: function (offset, callback) {
	console.log('PositionValueCharacteristic onReadRequest - offset=' + offset + ' ,callback=' + callback);

	var data = new Buffer(8);
	data.writeFloatLE(pswnCurrentPos.latitude, 0);
	data.writeFloatLE(pswnCurrentPos.longitude, 4);
        callback(this.RESULT_SUCCESS, data);
    },
    onSubscribe: function(maxValueSize, updateValueCallback) { 
	console.log('PositionValueCharacteristic onSubscribe - maxValueSize=' + maxValueSize + ' ,updateValueCallback=' + updateValueCallback);

	pswnNotifyCallback = updateValueCallback;
    },
    onUnsubscribe: function() {
    	console.log('PositionValueCharacteristic onUnsubscribe');

	pswnNotifyCallback = null;
    },
    onNotify: function() {
	console.log('PositionValueCharacteristic onNotify');
    }
});
};

util.inherits(PositionValueCharacteristic, BlenoCharacteristic);


// ----------------------------- Position Threshold Characteristic ----------------------------- //

var PositionThresholdCharacteristic = function () {
PositionThresholdCharacteristic.super_.call(this, {
    uuid: hub.nodes.rpi.sensors.PSWN.PositionThreshold.uuid,
    properties: ['write', 'writeWithoutResponse'],
    descriptors: [
        new BlenoDescriptor({
            uuid: '2901',
            value: hub.nodes.rpi.sensors.PSWN.PositionThreshold.descriptorValue
        })
    ],
    onWriteRequest: function (data, offset, withoutResponse, callback) {

    	console.log('PositionThresholdCharacteristic onWriteRequest - data=' + data.toString('hex') + ', offset=' + offset + ', withoutResponse=' + withoutResponse + ', callback=' + callback);
	
	pswnThreshold = data.readFloatLE(0);
	console.log('pswnThreshold: ' + pswnThreshold);

	callback(this.RESULT_SUCCESS);
    }
});
};

util.inherits(PositionThresholdCharacteristic, BlenoCharacteristic);




// ----------------------------- Display Value Characteristic ----------------------------- //

var DisplayValueCharacteristic = function () {
DisplayValueCharacteristic.super_.call(this, {
    uuid: hub.nodes.intel_galileo.actuators.DA.DisplayValue.uuid,
    properties: ['write', 'writeWithoutResponse'],
    descriptors: [
        new BlenoDescriptor({
            uuid: '2901',
            value: hub.nodes.intel_galileo.actuators.DA.DisplayValue.descriptorValue
        })
    ],
    onWriteRequest: function (data, offset, withoutResponse, callback) {

    	console.log('DisplayValueCharacteristic onWriteRequest - data=' + data.toString('hex') + ', offset=' + offset + ', withoutResponse=' + withoutResponse + ', callback=' + callback);

        port.write("\x07\x07"+data);
        port.drain();
    }
});
};

util.inherits(DisplayValueCharacteristic, BlenoCharacteristic);


// ----------------------------- Light Value Characteristic ----------------------------- //

var LightValueCharacteristic = function () {
LightValueCharacteristic.super_.call(this, {
    uuid: hub.nodes.intel_galileo.actuators.LA.LightValue.uuid,
    properties: ['write', 'writeWithoutResponse'],
    descriptors: [
        new BlenoDescriptor({
            uuid: '2901',
            value: hub.nodes.intel_galileo.actuators.LA.LightValue.descriptorValue
        })
    ],
    onWriteRequest: function (data, offset, withoutResponse, callback) {

    	console.log('LightValueCharacteristic onWriteRequest - data=' + data.toString('hex') + ', offset=' + offset + ', withoutResponse=' + withoutResponse + ', callback=' + callback);
        
	nrfNodeId = hub.nodes.intel_galileo.actuators.LA.NrfInfo.nrfNodeId;
	hwDeviceId = hub.nodes.intel_galileo.actuators.LA.NrfInfo.hwDeviceId;

	//hub.nodes.intel_galileo.actuators.LA.LightValue.writeCallFunction(nrfNodeId, hwDeviceId, data[0] == 0x01);

    if (data[0] == 0x00) {
        port.write("\x08\x09");
        port.drain();
    } else if (data[0] == 0x01) {
        port.write("\x08\x08");
        port.drain();
    }

    }
});
};

util.inherits(LightValueCharacteristic, BlenoCharacteristic);


// ----------------------------- Sound Value Characteristic ----------------------------- //

var SoundValueCharacteristic = function () {
SoundValueCharacteristic.super_.call(this, {
    uuid: hub.nodes.intel_galileo.actuators.SA.SoundValue.uuid,
    properties: ['write', 'writeWithoutResponse'],
    descriptors: [
        new BlenoDescriptor({
            uuid: '2901',
            value: hub.nodes.intel_galileo.actuators.SA.SoundValue.descriptorValue
        })
    ],
    onWriteRequest: function (data, offset, withoutResponse, callback) {

    	console.log('SoundValueCharacteristic onWriteRequest - data=' + data.toString('hex') + ', offset=' + offset + ', withoutResponse=' + withoutResponse + ', callback=' + callback);

	nrfNodeId = hub.nodes.intel_galileo.actuators.SA.NrfInfo.nrfNodeId;
	hwDeviceId = hub.nodes.intel_galileo.actuators.SA.NrfInfo.hwDeviceId;

	 if (data[0] == 0xff) {
         port.write("\x09\x0A");
         port.drain();
     }
    }
});
};

util.inherits(SoundValueCharacteristic, BlenoCharacteristic);


// ----------------------------- Test Characteristic ----------------------------- //

var TestCharacteristic = function () {
TestCharacteristic.super_.call(this, {
    uuid: 'FFFF',
    properties: ['read'],
    descriptors: [
        new BlenoDescriptor({
            uuid: '2901',
            value: 'TS:23:TestSensor'
        })
    ],
    onReadRequest: function (offset, callback) {
	console.log('TestCharacteristic onReadRequest - offset=' + offset + ' ,callback=' + callback);

	//var data = new Buffer("30");
	var data = new Buffer(4);
	data.writeFloatLE(30, 0);
        callback(this.RESULT_SUCCESS, data);
    }
});
};

util.inherits(TestCharacteristic, BlenoCharacteristic);


// ----------------------------- Create services and advertise them ----------------------------- //

// Creates the service(s) and the characteristics provided by the gateway inside each service
function MyServices() {
        MyServices.super_.call(this, {
            uuid: hub.ble.uuid,
            characteristics: [
		//new TestCharacteristic(),
		new PositionValueCharacteristic(),
		new PositionThresholdCharacteristic(),
		new SpeedValueCharacteristic(),
		new SpeedThresholdCharacteristic(),
		new DisplayValueCharacteristic(),
		new LightValueCharacteristic(),
		new SoundValueCharacteristic()
            ]
        });
}

util.inherits(MyServices, BlenoPrimaryService);


// ----------------------------- BLENO events ----------------------------- //

// Manage the advertising state based on the ble power state.
bleno.on('stateChange', function (state) {
        console.log('on -> stateChange: ' + state);

        if (state === 'poweredOn') {
            bleno.startAdvertising(hub.ble.name, [hub.ble.uuid]);
        } else {
            bleno.stopAdvertising();
        }
});

// A new device gets connected
bleno.on('accept', function () {
        console.log('on -> accept');

        bleno.updateRssi();
});

// Client gets disconnected
bleno.on('disconnect', function () {
        console.log('on -> disconnect');
});

bleno.on('rssiUpdate', function (rssi) {
        console.log('on -> rssiUpdate: ' + rssi);
});

// Inicio del advertising. Inicialización de los servicios
bleno.on('advertisingStart', function (error) {
        console.log('on -> advertisingStart: ' + (error ? 'error ' + error : 'success'));

        if (!error) {
            bleno.setServices([
//      new DeviceNameService,
                new MyServices()
            ]);
        }
});

// Fin advertising
bleno.on('advertisingStop', function () {
        console.log('on -> advertisingStop');
});

bleno.on('servicesSet', function () {
        console.log('on -> servicesSet');
});

console.log('BLE peripheral created.');