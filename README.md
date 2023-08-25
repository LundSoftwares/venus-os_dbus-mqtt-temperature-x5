# venus-os_dbus-mqtt-temperature-x5 - Emulates up to 5 separate temperature sensors in VenusOS from info in MQTT data

**First off, a big thanks to [mr-manuel](https://github.com/mr-manuel) that created a bunch of templates that made this possible**

GitHub repository: [LundSoftwares/venus-os_dbus-mqtt-temperature-x5](https://github.com/LundSoftwares/venus-os_dbus-mqtt-temperature-x5)

### Disclaimer
I'm not responsible for the usage of this script. Use on own risk! 


### Purpose
The script emulates up to 5 temperature sensors in Venus OS. It gets the MQTT data from a subscribed topic and publishes the information on the dbus as the service com.victronenergy.temperature.mqtt_temperature with the VRM instances from the Config file.


### Config
Copy or rename the config.sample.ini to config.ini in the dbus-mqtt-temperature folder and change it as you need it.

<details>
  
<summary>Example: Set number of instances to create, then change custom name, VRM Instance and type for all Sensors</summary>

```ruby
; Set number of Instances to create, 1 is minimum, 5 is maximum
; default: 1
instances = 1

;---------------------------------------------------------------------
; Device name #1
; default: MQTT Temperature
device_name = MQTT Temperature

; Device VRM instance #1
; default: 100
device_instance = 100

; Temperature type #1
; 0 = battery
; 1 = fridge
; 2 = generic
; default: 2
type = 2
```
</details>

#### JSON structure
<details>
<summary>Minimum required</summary> 
  
```ruby
{
"temperature": 22.0
}
```
</details>

<details>
<summary>Minimum required with humidity and pressure</summary> 
  
```ruby
{
    "temperature": 23,
    "humidity": 45,
    "pressure": 1002
}
```
</details>

<details>
<summary>Full</summary> 
  
```ruby
{
    "temperature": 23,
    "humidity": 45,
    "pressure": 1002,
    "temperature2": 20,
    "humidity2": 40,
    "pressure2": 1002,
    "temperature3": 26,
    "humidity3": 42,
    "pressure3": 1007,
    "temperature4": 15,
    "humidity4": 99,
    "pressur4": 1005,
    "temperature5": 4,
    "humidity5": 88,
    "pressure5": 1002
}
```
</details>


### Install
1. Copy the ```dbus-mqtt-temperature``` folder to ```/data/etc``` on your Venus OS device

2. Run ```bash /data/etc/dbus-mqtt-temperature/install.sh``` as root

The daemon-tools should start this service automatically within seconds.

### Uninstall
Run ```/data/etc/dbus-mqtt-temperature/uninstall.sh```

### Restart
Run ```/data/etc/dbus-mqtt-temperature/restart.sh```

### Debugging

The logs can be checked with ```tail -n 100 -F /data/log/dbus-mqtt-temperature/current | tai64nlocal```

The service status can be checked with svstat: ```svstat /service/dbus-mqtt-temperature```

This will output somethink like ```/service/dbus-mqtt-temperature: up (pid 5845) 185 seconds```

If the seconds are under 5 then the service crashes and gets restarted all the time. If you do not see anything in the logs you can increase the log level in ```/data/etc/dbus-mqtt-temperature/dbus-mqtt-temperature.py``` by changing ```level=logging.WARNING``` to ```level=logging.INFO``` or ```level=logging.DEBUG```

If the script stops with the message ```dbus.exceptions.NameExistsException: Bus name already exists: com.victronenergy.temperature.mqtt_temperature"``` it means that the service is still running or another service is using that bus name.

### Compatibility
It was tested on Venus OS Large ```v3.01``` on the following devices:

- RaspberryPi 3b+
- Simulated Temperature data sent from NodeRed

### NodeRed Example code

<details>
<summary>Import into NodeRed runing on your VenusOS device for some simple testing</summary> 
  
```ruby
[{"id":"df8b7f2fd88734d8","type":"mqtt out","z":"36b8e7c267cde307","name":"MQTT out","topic":"Temperature/Sensors","qos":"","retain":"","respTopic":"","contentType":"","userProps":"","correl":"","expiry":"","broker":"3cc159c0642d9663","x":720,"y":340,"wires":[]},{"id":"f845dc4f9a4ffa6e","type":"function","z":"36b8e7c267cde307","name":"function 2","func":"msg.payload=\n{\n    \"temperature\": 23,\n    \"humidity\": 45,\n    \"pressure\": 1002,\n    \"temperature2\": 20,\n    \"humidity2\": 40,\n    \"pressure2\": 1002,\n    \"temperature3\": 26,\n    \"humidity3\": 42,\n    \"pressure3\": 1007,\n    \"temperature4\": 15,\n    \"humidity4\": 99,\n    \"pressur4\": 1005,\n    \"temperature5\": 4,\n    \"humidity5\": 88,\n    \"pressure5\": 1002\n}\nreturn msg;","outputs":1,"noerr":0,"initialize":"","finalize":"","libs":[],"x":520,"y":340,"wires":[["df8b7f2fd88734d8"]]},{"id":"b6402e0e1f5a652f","type":"inject","z":"36b8e7c267cde307","name":"","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"30","crontab":"","once":true,"onceDelay":"1","topic":"","payload":"","payloadType":"date","x":350,"y":340,"wires":[["f845dc4f9a4ffa6e"]]},{"id":"3cc159c0642d9663","type":"mqtt-broker","name":"","broker":"localhost","port":"1883","clientid":"","autoConnect":true,"usetls":false,"protocolVersion":"4","keepalive":"60","cleansession":true,"birthTopic":"","birthQos":"0","birthPayload":"","birthMsg":{},"closeTopic":"","closeQos":"0","closePayload":"","closeMsg":{},"willTopic":"","willQos":"0","willPayload":"","willMsg":{},"userProps":"","sessionExpiry":""}]
```
</details>






### Screenshots

<details>
<summary>Device List</summary> 
  
![1](https://github.com/LundSoftwares/venus-os_dbus-mqtt-temperature-x5/assets/23386303/6601243c-6887-4464-98bf-60da35f158f2)

</details>

<details>
<summary>Device Status</summary> 
  
![2](https://github.com/LundSoftwares/venus-os_dbus-mqtt-temperature-x5/assets/23386303/f5378df5-96b9-41b5-ae34-d87bbea19bb7)

</details>

<details>
<summary>Front Page</summary> 
  
![3](https://github.com/LundSoftwares/venus-os_dbus-mqtt-temperature-x5/assets/23386303/208ace63-9677-426f-891b-0d0f57bf7c8b)

</details>



# Sponsor this project

<a href="https://www.paypal.com/donate/?business=MTXQ49TG6YH36&no_recurring=0&item_name=Like+my+work?+%0APlease+buy+me+a+coffee...&currency_code=SEK">
  <img src="https://pics.paypal.com/00/s/MjMyYjAwMjktM2NhMy00NjViLTg3N2ItMDliNjY3MjhiOTJk/file.PNG" alt="Donate with PayPal" />
</a>
