# MOTAM - Gateway

MOTAM - Gateway repository contains the applications of the vehicle's gateway on MOTAM platform.

The gateway collects all the road state and vehicles information from MOTAM infraestructure. This data is analized, parsed and send by a secure connection to AVATAR Android application.

Another MOTAM related repositories and more info about MOTAM project can be found on:
> [**MOTAM project website by NICS.**](https://www.nics.uma.es/projects/motam)

## Hardware list
MOTAM Gateway is supported by Raspberry Pi 3 Model B. 
Several peripherals are attached to Raspberry Pi in order to collect different kind of data from the own car, near vehicles and Road Side Units.
The peripherals are listed below:

 - Raspberry Pi 7" Touch Display.
 - ELM327 OBD II Interface.
 - BU-353S4 USB GPS Receiver from GlobalSat.
 - UPS PIco HV3.0B from PiModules.
 - nRF52840 dongle from NordicSemiconductor.

![MOTAM-Gateway](https://i.imgur.com/XAnsNOE.jpg)

## Usage
Just execute in Raspberry Pi terminal:

	cd ~/MOTAM-Gateway/
    sudo python3 startGateway.py
    
For help:

    sudo python3 startGateway.py --help
    
For Interactive Scanner mode (default location of beacons):

	sudo python3 startGateway.py --interactive

For Interactive Scanner mode and custom location coordinates of beacons:

	sudo python3 startGateway.py --interactive 36.715923 -4.477482

For capturing real data from OBDII and GPS receiver (must be connected to USB)

	sudo python3 startGateway.py --real_obd_gps

For loading a OBDII and GPS session trip (default session trip):

	sudo python3 startGateway.py --loadCarTrip

For loading an OBDII and GPS session trip (another session trip). The session trip must be located con simulation/sessions folder:

	sudo python3 startGateway.py --loadCarTrip alternativeSessionTrip.db

For loading an OBDII, GPS and captured beacons session trip (default trip):

	sudo python3 startGateway.py --loadCarTrip --loadBeaconsTrip

For using another type of vehicle (change certificate). Available: normal, emergency and slow vehicle:

	sudo python3 startGateway.py --cert pasarela_lento.crt

For capturing real BLE4 beacons with real receiver.

	sudo python3 startGateway.py --real_ble4

For capturing real BLE5 beacons with real receiver.

	sudo python3 startGateway.py --real_ble5

## Connection parameters
- Gateway IP direction: 192.168.0.1
- Gateway TLS port: 4443

## Simulation
MOTAM-Gateway can simulate a car trip in order to send simulated data to AVATAR app. 

It's possible to select the kind of data that is simulated and what data come from real sources. This may be useful for development and testing purpouses.

Here you can find a preloaded simulation of a car trip. The information is sent via Wifi Direct socket in JSON format.

Simulation has a duration of 155 seconds.

| Time (seconds) | Beacon data |
|--|--|
| 5 to 10 | Baby seat: No baby, not fastened |
| 10 to 15 | Baby seat: Baby, not fastened |
| 15 to 20 | Baby seat: Baby, fastened |
| 20 to 22 | Traffic light: green state (2 seconds left) |
| 23 to 25 | Traffic light: yellow state (2 seconds left) |
| 26 to 27 | Traffic light: red state (3 seconds left) |
| 30 to 40 | Emergency vehicle (from left side) |
| 50 to 60 | Crashed vehicle |

> The time is approximate and relative to the start of simulation

## Interactive Scanner mode
List of MOTAM beacons included in the Interactive mode:
- Baby seat: baby seated with not fastened belt.
- Baby seat: baby seated with fastened belt.
- Baby seat: baby not seated with not fastened belt.
- Traffic light in red state.
- Traffic light in yellow state.
- Traffic light in green state.
- Intelligent Traffic Light in red state 16 seconds left.
- Intelligent Traffic Light in yellow state 5 seconds left.
Intelligent Traffic Light in green state 29 seconds left.
- Dry road.
- Wet road.
- Frozen road.
- Bicycle in motion.
- Bicycle accident.
- Information panel "Incendio 2 Km"
- Information panel "Carrera ciclista"
- Pedestrian near.
- Slow Vehicle.
- Emergency vehicle moving on left road side.
- Emergency vehicle moving on center of the road.
- Emergency vehicle moving on right road side.

## Bluetooth 5 Beacon Scanner
The firmware of nRF52840 dongle Beacon Scanner can be found on its GitHub repository.

> [**MOTAM Scanner repository on GitHub.**](https://github.com/nicslabdev/MOTAM-Scanner)

## Changelog
### Version 3.7
- Fixed BLE4 bluepy error: HCI0 interface go down when it is scanning for too much time.
- Bug fixed when parsing time remaining data from intelligent traffic light.
- Added two new examples of Info Panel on interactive mode.
- Added support and parsed data from AVATAR for emergency vehicle, slow vehicle and crashed vehicle modes.
- Added new simulation database.

### Version 3.6
- Fixed bug: simulation database doesn't work
- Added new simulation DB for DEMO in UMA Campus, Málaga.
- Now, simulation is played in loop.
- Added support for real OBDII interface and GPS receiver.

### Version 3.5
- Deleted force request client certificate argument.
- Deleted client log dump argument.
- Deleted taking driver shots arguments. Now, this is not optional, gateway will take pictures if camera is connected
- User profile is downloaded from AVATAR.

### Version 3.4
- Updated AVATAR JSON for info Panel.
- Updated frame format: new beacons ID for sensors.
- Added examples of pedestrian, slow vehicle, emergency vehicle and crashed vehicle on interactive mode.
- Updated simulation DB (new frame format).

### Version 3.3
- Integrated OBDII GPS and beacons session (saved trip) support.

### Version 3.2
- Integrated Raspberry Pi Camera module
- Added script argument for taking pictures of driver
- User ID captured from certificate from AVATAR

### Version 3.1
- Integrated Wifi-Direct connection scripts to main Python script.
- Script adaptation to new Raspbian: Buster.
- Updated frame formats: certificates id 0, 1 and 2.
- Updated frame formats: Presence field on AVATAR JSON to true or false.
- Added new beacons frame examples on interactive mode.

### Version 3.0
- Major change: Renamed script to startGateway.py. Now, this is the main script that runs all the MOTAM Gateway functionalities.
- Added function for receiving data from socket. This will be used for receiving MOTAM user picture sent by AVATAR.
- Added interactive simulated BLE scanner. In this mode, you can simulate in real time the capture of predefined MOTAM beacons. It's possible to change the location of the simulated MOTAM beacons.
- Added command line arguments in order to activate the main execution modes what user want: BLE 4 Scanner, BLE 5 Scanner, Interactive simulated scanner, etc.
- Added command line arguments '--dump' for logging all the data received from AVATAR by socket for development purposes on 'client.log' file.
### Version 2.2
- Now sensor data and car_info is sent separately
### Version 2.1
- Added command line arguments for choosing IP Address of Gateway
### Version 2.0
- Deleted not secure socket connection.
- Added command line arguments.
- Now you can choose the sample rate of the simulation.
- Now you can choose by command line argument the simulated session database.
- Now you can choose the gateway certificate by command line.
- Now you can choose the CA certificate by command line.
### Version 1.3
- Added support for receive data through socket. Now, AVATAR can send commands to Gateway.
### Version 1.2
- Added two connection options. It is possible client receives simulation data by TLS connection through TLS port or by an unsecure connection through unsafe port.
### Version 1.1
- Code migrated to Python 3.
- Added Transport Layer Security (TLS) to connection between gateway and smartphone.
### Version 1.0
First version of simulation script.

## To Do list
- Integrate load session simulation code.
- Integrate BLE5 real scanner.
