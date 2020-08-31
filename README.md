# SwitchBot Meter Readings
Python script to read temperature, humidity and battery from a Switchbot Meter device, and then make the data accessible via a API on your local network. The script has been tested on a Raspberry Pi Zero W using Raspberry Pi OS.

You will need:
1. Python3
2. [SwitchBot Thermometer](https://www.amazon.co.uk/SwitchBot-Thermometer-Hygrometer-Alexa-iPhone/dp/B07L4QNZVF/ref=sr_1_2?dchild=1&keywords=switchbot+meter&qid=1598878292&sr=8-2)
3. [BluePy](https://github.com/IanHarvey/bluepy)
4. [Flask](https://github.com/pallets/flask)
5. [TinyDb](https://github.com/msiemens/tinydb)

## Getting Started

### Use Cases

- View your air quality data within the iOS Home app by using [HomeBridge](https://homebridge.io/) and the **[homebridge-http-humidity-sensor](https://github.com/Supereg/homebridge-http-humidity-sensor)** plugin.


### Install

1. Install Python3 and Pip3: `sudo apt-get install python3 python3-pip`
2. Install BluePy (Bluetooth Framework):  `sudo pip3 install bluepy`
3. Install Flask (API Framework): `sudo pip3 install -U Flask`
4. Install TinyDb (Storage): `sudo pip3 install tinydb`
5. Run the script: `sudo python3 meters.py`

### SwitchBot Configuration

To locate your SwitchBot Meter by Bluetooth in the local area, the MAC address and name of the meter reading is required. You can find this information within the SwitchBot mobile application. Once found, set the following variables with the values from your device.

```python
# SwitchBot Meter Configuration
METER_ROOMS = ['Bedroom']
METER_MACS = ['e8:fe:50:d1:75:dd']
```

### API Configuration

By default, the API will be accessible via the network port 5000. To change this, along with the hostname of the API server, set the following configuration with your values.

```python
# API Configuration
API_HOST="localhost"
API_PORT=5000
```

## API Methods

### '/meters' - All Meter Devices

#### Request

```http
GET /meters HTTP/1.1
Host: 192.168.1.233:5000
```

#### Response

```json
[
    {
        "time": "2020-08-31 13:38:24",
        "room": "Bedroom",
        "temperature": "22.5",
        "humidity": "65",
        "battery": "100"
    }
]
```

### '/meters/room' - Get Meter Device by Name

#### Request

```http
GET /meters/Bedroom HTTP/1.1
Host: 192.168.1.233:5000
```

#### Response

```json
{
    "time": "2020-08-31 23:40:03",
    "room": "Bedroom",
    "temperature": "24.4",
    "humidity": "65",
    "battery": "100"
}
```