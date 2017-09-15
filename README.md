# **MOTAM - [Raspberry Pi]** #

En este repositorio se encuentran los desarrollos finales sobre las plataforma Raspberry Pi, tanto los desarrollos relativos a los dispositivos (sensores) DEPHISIT conectados a esta plataforma como los relativos a la pasarela de comunicación entre NRF24 y BLE.


# Descripción de los distintos ficheros desarrollados #

A continuación se comentan los distintos ficheros Node.JS relacionados con estos desarrollos, tanto aquellos con funcionalidad real como los creados para la realización de simulaciones:

- Fichero *PositionSensorBasedOnGPSD.js*. Definición e implementación de un sensor de posición basado en las lecturas proporcionadas por el servicio "gpsd" de Linux, al que se ha conectado el GPS receptor [BU-353S4](http://usglobalsat.com/p-688-bu-353-s4.aspx) (PositionSensorBasedOnGPSD). Hace uso del módulo "[node-gpsd](https://www.npmjs.com/package/node-gpsd)" de Node.JS.

- Fichero *pswnThread.js*. Hebra para la notificación de los nuevos valores proporcionados por el dispositivo PositionSensor[WithNotifications] al proceso principal. Hace uso del módulo "[util](https://nodejs.org/api/util.html)" de Node.JS.

- Fichero *SpeedSensorBasedOnSerialOBD.js*. Definición e implementación de un sensor de velocidad basado en un lector serie [OBD-II](http://www.amazon.es/Interfaz-Diagnostico-Lector-Codigos-Diagnosis/dp/B00CNZNSYA/ref=sr_1_4?ie=UTF8&qid=1454340665&sr=8-4&keywords=ELM327+usb) (SpeedSensorBasedOnSerialOBD). Hace uso del módulo "[serial-obd](https://www.npmjs.com/package/serial-obd)" de Node.JS.

- Fichero *sswnThread.js*. Hebra para la notificación de los nuevos valores proporcionados por el dispositivo SpeedSensor[WithNotifications] al proceso principal. Hace uso del módulo "[util](https://nodejs.org/api/util.html)" de Node.JS.

- Fichero *NRF_Communication.js*. Definición e implementación del núcleo de la pasarela encargada de presentar los dispositivos basados en NRF24 como dispositivos BLE para que puedan ser detectados y usados por el servicio Android. Hace uso de los módulos "[nrf](https://www.npmjs.com/package/nrf)",  "[crypto](https://nodejs.org/api/crypto.html)" y "[unidecode](https://www.npmjs.com/package/unidecode)" de Node.JS.

- Fichero *BLE_PSWNDevice_SSWNDevice_DA_LA_SA.js*. Definición e implementación de los dispositivos DEPHISIT de tipo PositionSensorWithNotifications, SpeedSensorWith hNotifications, DisplayActuator, LightActuator y SoundActuator a través de BLE, y haciendo uso de la pasarela NRF24-BLE. Hace uso de los módulos "[util](https://nodejs.org/api/util.html)" , "[child_process](https://nodejs.org/api/child_process.html)" y "[bleno](https://www.npmjs.com/package/bleno)" de Node.JS, así como de los ficheros  "pswnThread.js", "sswnThread.js" y "NRF_Communication.js" comentados más arriba.

- Fichero *Dispositivos simulados/BLE_Simulated_PSWNDevice_SSWNDevice_DA_LA_SA.js*. Definición e implementación de los dispositivos DEPHISIT simulados de tipo PositionSensorWithNotifications, SpeedSensorWithNotifications, DisplayActuator, LightActuator y SoundActuator a través de BLE.

- Fichero *Dispositivos simulados/BLE_SimulatedXXWNDevice.js*. Definición e implementación de un dispositivo DEPHISIT simulado con notificaciones (XXWNDevice) a través de BLE.

- Fichero *Dispositivos simulados/simulated-NRF_Communication.js*. Definición e implementación simulada del núcleo de la pasarela NRF24-BLE 

- Fichero *Dispositivos simulados/simulated-pswnThread.js*. Simulación de la hebra encargada de notificar los nuevos valores proporcionados por el dispositivo PositionSensor[WithNotifications] al proceso principal.

- Fichero *Dispositivos simulados/simulated-sswnThread.js*. Simulación de la hebra encargada de notificar los nuevos valores proporcionados por el dispositivo SpeedSensor[WithNotifications] al proceso principal.
