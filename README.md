# **MOTAM - [Raspberry Pi]** #

En este repositorio se encuentran los desarrollos sobre la pasarela, alojada en la plataforma Raspberry Pi.


# Descripción de los distintos ficheros desarrollados #

Existen ficheros Node.JS y scripts de Python. Node.JS llama a estos scripts de Python cuando es necesario que realicen ciertas tareas.

A continuación se comentan los distintos ficheros relacionados con estos desarrollos, tanto aquellos con funcionalidad real como los creados para la realización de simulaciones:

- Fichero *BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js*. Este es el código principal. Contiene la definición e implementación de los dispositivos MOTAM de tipo PositionSensorWithNotifications, SpeedSensorWithNotifications, DisplayActuator, LightActuator y SoundActuator a través de BLE, y haciendo uso del puerto serie. Hace uso de los ficheros "pswnThread.js" y "sswnThread.js". También utiliza los módulos "[util](https://nodejs.org/api/util.html)" , "[child_process](https://nodejs.org/api/child_process.html)" y "[bleno](https://www.npmjs.com/package/bleno)" de Node.JS.

- Fichero *pswnThread.js*. Hebra lanzada por BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js para la notificación de los nuevos valores proporcionados por el dispositivo PositionSensor[WithNotifications] al proceso principal. Hace uso del fichero PositionSensorBasedOnGPSD.js y del módulo "[util](https://nodejs.org/api/util.html)" de Node.JS.

- Fichero *PositionSensorBasedOnGPSD.js*. Definición e implementación de un sensor de posición basado en las lecturas proporcionadas por el servicio "gpsd" de Linux, al que se ha conectado el GPS receptor [BU-353S4](http://usglobalsat.com/p-688-bu-353-s4.aspx) (PositionSensorBasedOnGPSD). Hace uso del módulo "[node-gpsd](https://www.npmjs.com/package/node-gpsd)" de Node.JS.

- Fichero *sswnThread.py*. Script de python. Hebra lanzada por BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js para la notificación de los nuevos valores proporcionados por el GPS.