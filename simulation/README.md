
# Gateway simulation

Here you can find a preloaded simulation of a car trip. The information is sent via Wifi Direct socket in JSON format.

Although the simulation has a duration of 155 seconds, it's reproduced in loop. So script doesn't stop.

## Simulated beacons deployed

| Time (seconds) | Beacon data |
|--|--|
| 10 to 20 | Baby seat: Insecure |
| 20 to 30 | Baby seat: Secure |
| 50 to 60 | Traffic light: Green |
| 80 to 90 | Road state: dry | 
| 110 to 120 | Bicicle: moving |

> The time here shown is approximate and relative to the start of simulation

## Usage

Just execute in Raspberry Pi terminal:

    python3 /home/pi/MOTAM/simulation/startSimulation.py

## Connection parameters:

 - Gateway IP direction: 192.168.0.1
 - Gateway TLS port: 4443
 - Gateway no secure port: 9999

## Changelog
### Version 1.2
 - Added two connection options. It is possible to receive simulation data by TLS connection through TLS port or by an unsecure connection through unsafe port.
### Version 1.1
 - Code migrated to Python 3.
 - Added Transport Layer Security (TLS) to connection between gateway and smartphone.
### Version 1.0
First version of simulation script.