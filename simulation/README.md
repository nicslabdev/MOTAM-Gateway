
# Gateway simulation

Here you can find a preloaded simulation of a car trip. The information is sent via Wifi Direct socket in JSON format.

Simulation has a duration of 155 seconds.

## Simulated beacons deployed

| Time (seconds) | Beacon data |
|--|--|
| 5 to 10 | Baby seat: No baby, not fastened |
| 10 to 15 | Baby seat: Baby, not fastened |
| 15 | Baby seat: Baby, fastened |
| 20 to 22 | Traffic light: green state (2 seconds left) |
| 23 to 25 | Traffic light: yellow state (2 seconds left) |
| 26 to 27 | Traffic light: red state (3 seconds left) |
| 30 to 40 | Emergency vehicle (from left side) |
| 50 to 60 | Crashed vehicle |

> The time is approximate and relative to the start of simulation

## Usage

Just execute in Raspberry Pi terminal:

    python3 /home/pi/MOTAM/simulation/startSimulation.py

## Connection parameters

- Gateway IP direction: 192.168.0.1
- Gateway TLS port: 4443