# **MOTAM - Gateway** #

In this repository you can find all gateway elements and its development. The gateway is supported by Raspberry Pi 3 Model B platform.


# Description of every developed file #

There are several Node.JS files, Python scripts and bash scripts. The main code is written in Node.JS. Node.JS code calls to the other scripts when it is neccesary to make certain tasks.

Every file related with the gateway (those used for real functionality and those used for simulation) are stated below:

- *BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js* file. This is the main code. Here is the definition and implementation of the MOTAM devices, i.e: PositionSensorWithNotifications, SpeedSensorWithNotifications, DisplayActuator, LightActuator and SoundActuator. This actuators and sensors work through BLE and serial port. Main code uses "[util](https://nodejs.org/api/util.html)", "[child_process](https://nodejs.org/api/child_process.html)", "[bleno](https://www.npmjs.com/package/bleno)" and [serialport](https://www.npmjs.com/package/serialport) Node.JS modules.

- *package.json* file. Necessary for installation of Node.JS modules. Include a list of all necessary Node.JS modules used in MOTAM project.

- *MOTAM* file. This is a desktop shortcut for Debian environments. This should be located in the Desktop (/home/pi/Desktop/). If you double-click on it, this call "StartGateway.sh" script in "util" folder.



In *util* folder:

- *pswnThread.js* file. Thread launched by main code ("BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js"). This is used for new values notification from PositionSensor[WithNotifications] device. This use "PositionSensorBasenOnGPSD.js" file and "[util](https://nodejs.org/api/util.html)" Node.JS module.

- *PositionSensorBasedOnGPSD.js* file. Definition and implementation of a position sensor based on data from "gpsd" Linux service. A GPS receptor (BU-353S4) is connected to this Linux service. This use "[node-gpsd](https://www.npmjs.com/package/node-gpsd)" Node.js module

- *sswnThread.py* file. Python Script. This is a thread launched by main code (BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js) that notify the new values from GPS receiver.

- *loadSession.py* file. Old python script. This is not in use now. This thread can be launch by BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js process. The script charge a previously saved session for simulate a car trip. Sessions contains information about OBD-II interface and GPS, that has been captured in a previous car trip.

- *loadSessionSocket.py* file. Python Script. This charge a previously saved session for simulate a car trip and send the information in "real time" through a socket (ideally, through Wifi Direct). Sessions contains information about OBD-II interface and GPS, that has been captured in a previous car trip.


- *usbDiscovery* file. Bash script that return the identifier and path of the USB connected devices. This is used by the main code.

- *zenity* file. It's a simple shell script that show a GUI dialog about run OBDII interface simulator and return the answer to the main code. This is used by the main code.

- *StartGateway.sh* file. This is a bash script that start the main code "BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js" with super-user permission. This is called by MOTAM desktop shortcut.



In *docs* folder:

- *MOTAM Platform - Instalation and deployment guide_es* document. This document describes how to install and deploy all components fromt the MOTAM platform.

- *JSON example - ble_scan* text file. This is a example of the JSON format used between the gateway and the smartphone for sending data about MOTAM sensors detected.

- *JSON example - loadSessionSocket* text file. This is a example of the JSON format used between the gateway and the smartphone for sending data about a OBDII-GPS session (simulated trip).



In *sessions* folder:

Contains sessions, aka, data from GPS and OBD-II interface captured in previous car trips. Sessions are sqlite databases saved with obdgpslogger utility.

Currently, there are two sessions logged:



In *public* folder:
Contains files than can be downloaded from smartphone through Wifi_Direct. Only for Wifi_Direct tests.

- *UMA-5_10_17.db:* this is a log of a trip with a duration of 5'49''. No sensors in this session.

- *UMA-5_10_17-Short-WithSensors.db:* this is a short version of "UMA-5_10_17.db" with sensors. This sensors have beed added manually in the database. So this isn't real sensors, but its behaviour is like real sensors. This log has a duration of 2'35''. The sensors appears in the following times:

-- From 0'' to 11'': Bicycle moving sensor and green traffic light.
-- From 19'' to 30'': Stop sign
-- From 1'05'' to 1'25'': yellow traffic light
-- From 1'45'' to 1'56'': snow in road


In *wifi_pruebas* folder:
This is an early implementation of Wifi_Direct funcionality. This will be integrated in the rest of MOTAM code in the future. The static IP assigned to the Gateway is 192.168.0.1.

- *start.sh* file. This is a bash script that creates a Wifi_Direct connection and start a dhcp server.

- *stop.sh* file. This is a bash script that restore wifi configuration to default after creating a Wifi_Direct connection.

- *p2p_supplicant.conf* file. This is a configuration file used for configure Wifi_Direct connection.

- *udhcpd.conf* file. This is a configuration file used for configure DHCP server (neccesary for establish Wifi_Direct connection).



In *ble_pruebas* folder:
This is an early implementation of Bluetooth Low Energy scanning funcionality. This will be integrated in the rest of MOTAM code in the future.

- *ble_scan.py* file. Python script that scan MOTAM sensors (using BLE). The script detects beacons from BLE devices and decode those what contains MOTAM identifier. After that, encode the information of every beacon in a JSON. This JSON is sent through Wifi Direct socket. The JSON format can be seen in "docs" folder.