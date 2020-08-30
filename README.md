# Switchbot_Py_Meter
Python script to read temperature, humidity and battery from Switchbot Meter and send via MQTT (for Home Assistant etc). I am running on a Raspberry Pi Zero W under Raspbian.

You will need:
1. Python3
2. BluePy library (https://github.com/IanHarvey/bluepy)
3. Paho MQTT Library (https://github.com/eclipse/paho.mqtt.python)

Edit meters.py to add your configuration information:
1. Switchbot Meter Mac Addresses & "rooms".
2. MQTT Server address & login
3. Once running OK, change debug_level to 0. 

MQTT Topic example:
```
room1/meter
```
Payload example:
```
room1/meter: {"time":"2019-12-27 11:44:36","temperature":20.2,"humidity":57,"battery":100}
```

Home Assistant configuration.yaml example
```
- platform: mqtt
    unique_id: "room1_meter"
    name: "Room 1 Meter"
    state_topic: "room1/meter"
    value_template: "{{ value_json.temperature }}"
    unit_of_measurement: "°C"
  - platform: mqtt
    unique_id: "room1_meter_humidity"
    name: "Room 1 Meter Humidity"
    state_topic: "room1/meter"
    value_template: "{{ value_json.humidity }}"
  - platform: mqtt
    unique_id: "room1_meter_time"
    name: "Room 1 Meter Last Update"
    state_topic: "room1/meter"
    value_template: "{{ value_json.time }}"
  - platform: mqtt
    unique_id: "room1_meter_battery"
    name: "Room 1 Meter Battery"
    state_topic: "room1/meter"
    value_template: "{{ value_json.battery }}"

```

Run command is: 
Sudo Python3 meters.py

I run the script every 5 minutes using /etc/crontab. Add the line below to /etc/crontab
```
*/5 *   * * *   pi      sudo python3 /home/pi/Switchbot_Py_Meter/meters/meters.py >> /home/pi/Switchbot_Py_Meter/meters.log 2>&1
```
