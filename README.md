# **MOTAM - Gateway** #

In this repository you can find all the gateway elements and its development. The gateway is supported by Raspberry Pi 3 Model B platform.


# Description of every developed file #

There are several Node.JS files, Python scripts and bash scripts. The main code is written in Node.JS. Node.JS code calls to the other scripts when it is neccesary to make certain tasks.

Every file related with the gateway (those used for real functionality and those used for simulation) are stated below:

- *BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js* file. This is the main code. Here is the definition and implementation of the MOTAM devices, i.e: PositionSensorWithNotifications, SpeedSensorWithNotifications, DisplayActuator, LightActuator and SoundActuator. This actuators and sensors work through BLE and serial port. Main code uses "[util](https://nodejs.org/api/util.html)", "[child_process](https://nodejs.org/api/child_process.html)", "[bleno](https://www.npmjs.com/package/bleno)" and [serialport](https://www.npmjs.com/package/serialport) Node.JS modules.

- *package.json* file. Necessary for installation of Node.JS modules.

- Fichero *MOTAM*. Se trata de un acceso directo. Debe estar colocado en el escritorio (/home/pi/Desktop/). Al hacer doble click sobre él, llama al script de bash "Start.sh", que arranca el script principal.



In *util* folder:

- Fichero *pswnThread.js*. Hebra lanzada por BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js para la notificación de los nuevos valores proporcionados por el dispositivo PositionSensor[WithNotifications] al proceso principal. Hace uso del fichero PositionSensorBasedOnGPSD.js y del módulo "[util](https://nodejs.org/api/util.html)" de Node.JS.

- Fichero *PositionSensorBasedOnGPSD.js*. Definición e implementación de un sensor de posición basado en las lecturas proporcionadas por el servicio "gpsd" de Linux, al que se ha conectado el GPS receptor [BU-353S4](http://usglobalsat.com/p-688-bu-353-s4.aspx) (PositionSensorBasedOnGPSD). Hace uso del módulo "[node-gpsd](https://www.npmjs.com/package/node-gpsd)" de Node.JS.

- Fichero *sswnThread.py*. Script de Python. Hebra lanzada por BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js para la notificación de los nuevos valores proporcionados por el GPS.

- *loadSession.py*. Python script. This thread can be launch by BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js process. The script charge a previously saved session for simulate a car trip. Sessions contains information about OBD-II interface and GPS, that has been captured in a previous car trip.

- Fichero *usbDiscovery*. Se trata de un script de bash que devuelve el identificador y las rutas de los dispositivos conectados por USB. Es usado por el código principal.

- Fichero *zenity*. It's a simple shell script that show a GUI dialog about run OBDII interface simulator and return the answer to the main code. This is used by the main code.

- Fichero *Start.sh*. Es un script de bash que simplemente ejecuta el script principal "BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js" con permisos de superusuario.



En la carpeta docs:

- Document *MOTAM Platform - Instalation and deployment guide_es*. This document describes how to install and deploy all components fromt the MOTAM platform.



In *sessions* folder:

Contains sessions, aka, data from GPS and OBD-II interface captured in previous car trips. Sessions are sqlite databases saved with obdgpslogger utility.