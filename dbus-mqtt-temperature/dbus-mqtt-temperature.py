#!/usr/bin/env python

from gi.repository import GLib  # pyright: ignore[reportMissingImports]
import platform
import logging
import sys
import os
from time import sleep, time
import json
import paho.mqtt.client as mqtt
import configparser  # for config/ini file
import _thread
import dbus

# import Victron Energy packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "ext", "velib_python"))
from vedbus import VeDbusService


class SystemBus(dbus.bus.BusConnection):
    def __new__(cls):
        return dbus.bus.BusConnection.__new__(cls, dbus.bus.BusConnection.TYPE_SYSTEM)

class SessionBus(dbus.bus.BusConnection):
    def __new__(cls):
        return dbus.bus.BusConnection.__new__(cls, dbus.bus.BusConnection.TYPE_SESSION)
        
def dbusconnection():
    return SessionBus() if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else SystemBus()

# get values from config.ini file
try:
    config_file = (os.path.dirname(os.path.realpath(__file__))) + "/config.ini"
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        if config["MQTT"]["broker_address"] == "IP_ADDR_OR_FQDN":
            print(
                'ERROR:The "config.ini" is using invalid default values like IP_ADDR_OR_FQDN. The driver restarts in 60 seconds.'
            )
            sleep(60)
            sys.exit()
    else:
        print(
            'ERROR:The "'
            + config_file
            + '" is not found. Did you copy or rename the "config.sample.ini" to "config.ini"? The driver restarts in 60 seconds.'
        )
        sleep(60)
        sys.exit()

except Exception:
    exception_type, exception_object, exception_traceback = sys.exc_info()
    file = exception_traceback.tb_frame.f_code.co_filename
    line = exception_traceback.tb_lineno
    print(
        f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
    )
    print("ERROR:The driver restarts in 60 seconds.")
    sleep(60)
    sys.exit()


# Get logging level from config.ini
# ERROR = shows errors only
# WARNING = shows ERROR and warnings
# INFO = shows WARNING and running functions
# DEBUG = shows INFO and data/values
if "DEFAULT" in config and "logging" in config["DEFAULT"]:
    if config["DEFAULT"]["logging"] == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
    elif config["DEFAULT"]["logging"] == "INFO":
        logging.basicConfig(level=logging.INFO)
    elif config["DEFAULT"]["logging"] == "ERROR":
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.WARNING)


# get timeout
if "DEFAULT" in config and "timeout" in config["DEFAULT"]:
    timeout = int(config["DEFAULT"]["timeout"])
else:
    timeout = 60


# get type
if "DEFAULT" in config and "type" in config["DEFAULT"]:
    type = int(config["DEFAULT"]["type"])
else:
    type = 2
    
# get type 2
if "DEFAULT" in config and "type2" in config["DEFAULT"]:
    type2 = int(config["DEFAULT"]["type2"])
else:
    type2 = 2

# get type 3
if "DEFAULT" in config and "type3" in config["DEFAULT"]:
    type3 = int(config["DEFAULT"]["type3"])
else:
    type3 = 2
    
# get type 4
if "DEFAULT" in config and "type4" in config["DEFAULT"]:
    type4 = int(config["DEFAULT"]["type4"])
else:
    type4 = 2
    
# get type 5
if "DEFAULT" in config and "type5" in config["DEFAULT"]:
    type5 = int(config["DEFAULT"]["type5"])
else:
    type5 = 2
    
    
    
# set variables
connected = 0

last_changed = 0
last_updated = 0
temperature = -999
humidity = None
pressure = None

last_changed2 = 0
last_updated2 = 0
temperature2 = -999
pressure2 = None
humidity2 = None

last_changed3 = 0
last_updated3 = 0
temperature3 = -999
pressure3 = None
humidity3 = None

last_changed4 = 0
last_updated4 = 0
temperature4 = -999
pressure4 = None
humidity4 = None

last_changed5 = 0
last_updated5 = 0
temperature5 = -999
pressure5 = None
humidity5 = None

# MQTT requests
def on_disconnect(client, userdata, rc):
    global connected
    logging.warning("MQTT client: Got disconnected")
    if rc != 0:
        logging.warning(
            "MQTT client: Unexpected MQTT disconnection. Will auto-reconnect"
        )
    else:
        logging.warning("MQTT client: rc value:" + str(rc))

    while connected == 0:
        try:
            logging.warning("MQTT client: Trying to reconnect")
            client.connect(config["MQTT"]["broker_address"])
            connected = 1
        except Exception as err:
            logging.error(
                f"MQTT client: Error in retrying to connect with broker ({config['MQTT']['broker_address']}:{config['MQTT']['broker_port']}): {err}"
            )
            logging.error("MQTT client: Retrying in 15 seconds")
            connected = 0
            sleep(15)


def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        logging.info("MQTT client: Connected to MQTT broker!")
        connected = 1
        client.subscribe(config["MQTT"]["topic"])
    else:
        logging.error("MQTT client: Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    try:
        global last_changed, temperature, humidity, pressure, last_changed2, temperature2, humidity2, pressure2, last_changed3, temperature3, humidity3, pressure3, last_changed4, temperature4, humidity4, pressure4, last_changed5, temperature5, humidity5, pressure5

        # get JSON from topic
        if msg.topic == config["MQTT"]["topic"]:
            if msg.payload != "" and msg.payload != b"":
                jsonpayload = json.loads(msg.payload)

                if "temperature" in jsonpayload or "value" in jsonpayload:
                    last_changed = int(time())
                    if "temperature" in jsonpayload:
                        temperature = float(jsonpayload["temperature"])
                    elif "value" in jsonpayload:
                        temperature = float(jsonpayload["value"])

                    # check if humidity exists
                    if "humidity" in jsonpayload:
                        humidity = float(jsonpayload["humidity"])

                    # check if pressure exists
                    if "pressure" in jsonpayload:
                        pressure = float(jsonpayload["pressure"])
              
                    if "temperature2" in jsonpayload:
                        last_changed2 = int(time())
                        temperature2 = float(jsonpayload["temperature2"])
                        
                    # check if humidity exists
                    if "humidity2" in jsonpayload:
                        humidity2 = float(jsonpayload["humidity2"])

                    # check if pressure exists
                    if "pressure2" in jsonpayload:
                        pressure2 = float(jsonpayload["pressure2"])
                        
                    if "temperature3" in jsonpayload:
                        last_changed3 = int(time())
                        temperature3 = float(jsonpayload["temperature3"])
                        
                    # check if humidity exists
                    if "humidity3" in jsonpayload:
                        humidity3 = float(jsonpayload["humidity3"])

                    # check if pressure exists
                    if "pressure3" in jsonpayload:
                        pressure3 = float(jsonpayload["pressure3"]) 

                    if "temperature4" in jsonpayload:
                        last_changed4 = int(time())
                        temperature4 = float(jsonpayload["temperature4"])
                        
                    # check if humidity exists
                    if "humidity4" in jsonpayload:
                        humidity4 = float(jsonpayload["humidity4"])

                    # check if pressure exists
                    if "pressure4" in jsonpayload:
                        pressure4 = float(jsonpayload["pressure4"])

                    if "temperature5" in jsonpayload:
                        last_changed5 = int(time())
                        temperature5 = float(jsonpayload["temperature5"])
                        
                    # check if humidity exists
                    if "humidity5" in jsonpayload:
                        humidity5 = float(jsonpayload["humidity5"])

                    # check if pressure exists
                    if "pressure5" in jsonpayload:
                        pressure5 = float(jsonpayload["pressure5"])                        

                else:
                    logging.error(
                        'Received JSON MQTT message does not include a temperature object. Expected at least: {"temperature": 22.0} or {"value": 22.0}'
                    )
                    logging.debug("MQTT payload: " + str(msg.payload)[1:])
                    
            else:
                logging.warning(
                    "Received JSON MQTT message was empty and therefore it was ignored"
                )
                logging.debug("MQTT payload: " + str(msg.payload)[1:])

    except ValueError as e:
        logging.error("Received message is not a valid JSON. %s" % e)
        logging.debug("MQTT payload: " + str(msg.payload)[1:])

    except Exception as e:
        logging.error("Exception occurred: %s" % e)
        logging.debug("MQTT payload: " + str(msg.payload)[1:])


class DbusMqttTemperatureService:
    def __init__(
        self,
        servicename,
        deviceinstance,
        paths,
        productname="MQTT Temperature",
        customname="MQTT Temperature",
        connection="MQTT Temperature service",
    ):
        self._dbusservice = VeDbusService(servicename,dbusconnection())
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path("/Mgmt/ProcessName", __file__)
        self._dbusservice.add_path(
            "/Mgmt/ProcessVersion",
            "Unkown version, and running on Python " + platform.python_version(),
        )
        self._dbusservice.add_path("/Mgmt/Connection", connection)

        # Create the mandatory objects
        self._dbusservice.add_path("/DeviceInstance", deviceinstance)
        self._dbusservice.add_path("/ProductId", 0xFFFF)
        self._dbusservice.add_path("/ProductName", productname)
        self._dbusservice.add_path("/CustomName", customname)
        self._dbusservice.add_path("/FirmwareVersion", "0.0.1 (20230823)")
        # self._dbusservice.add_path('/HardwareVersion', '')
        self._dbusservice.add_path("/Connected", 1)

        self._dbusservice.add_path("/Status", 0)
        self._dbusservice.add_path("/TemperatureType", type)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path,
                settings["initial"],
                gettextcallback=settings["textformat"],
                writeable=True,
                onchangecallback=self._handlechangedvalue,
            )

        GLib.timeout_add(1000, self._update)  # pause 1000ms before the next request

    def _update(self):
        global last_changed, last_updated

        now = int(time())

        if last_changed != last_updated:
            self._dbusservice["/Temperature"] = (
                round(temperature, 2) if temperature is not None else None
            )
            self._dbusservice["/Humidity"] = (
                round(humidity, 2) if humidity is not None else None
            )
            self._dbusservice["/Pressure"] = (
                round(pressure, 0) if pressure is not None else None
            )

            log_message = "Temperature: {:.1f} °C".format(temperature)
            log_message += (
                " - Humidity: {:.1f} %".format(humidity) if humidity is not None else ""
            )
            log_message += (
                " - Pressure: {:.1f} hPa".format(pressure)
                if pressure is not None
                else ""
            )
            logging.debug(log_message)

            last_updated = last_changed

        # quit driver if timeout is exceeded
        if timeout != 0 and (now - last_changed) > timeout:
            logging.error(
                "Driver stopped. Timeout of %i seconds exceeded, since no new MQTT message was received in this time."
                % timeout
            )
            sys.exit()

        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice["/UpdateIndex"] + 1  # increment index
        if index > 255:  # maximum value of the index
            index = 0  # overflow from 255 to 0
        self._dbusservice["/UpdateIndex"] = index
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change


class DbusMqttTemperatureService2:
    def __init__(
        self,
        servicename,
        deviceinstance,
        paths,
        productname="MQTT Temperature 2",
        customname="MQTT Temperature 2",
        connection="MQTT Temperature service 2",
    ):
        self._dbusservice = VeDbusService(servicename,dbusconnection())
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path("/Mgmt/ProcessName", __file__)
        self._dbusservice.add_path(
            "/Mgmt/ProcessVersion",
            "Unkown version, and running on Python " + platform.python_version(),
        )
        self._dbusservice.add_path("/Mgmt/Connection", connection)

        # Create the mandatory objects
        self._dbusservice.add_path("/DeviceInstance", deviceinstance)
        self._dbusservice.add_path("/ProductId", 0xFFFF)
        self._dbusservice.add_path("/ProductName", productname)
        self._dbusservice.add_path("/CustomName", customname)
        self._dbusservice.add_path("/FirmwareVersion", "0.0.1 (20230823)")
        # self._dbusservice.add_path('/HardwareVersion', '')
        self._dbusservice.add_path("/Connected", 1)

        self._dbusservice.add_path("/Status", 0)
        self._dbusservice.add_path("/TemperatureType", type2)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path,
                settings["initial"],
                gettextcallback=settings["textformat"],
                writeable=True,
                onchangecallback=self._handlechangedvalue,
            )

        GLib.timeout_add(1000, self._update)  # pause 1000ms before the next request

    def _update(self):
        global last_changed2, last_updated2

        now = int(time())

        if last_changed2 != last_updated2:
            self._dbusservice["/Temperature"] = (
                round(temperature2, 2) if temperature2 is not None else None
            )
            self._dbusservice["/Humidity"] = (
                round(humidity2, 2) if humidity2 is not None else None
            )
            self._dbusservice["/Pressure"] = (
                round(pressure2, 2) if pressure2 is not None else None
            )

            log_message = "Temperature: {:.1f} °C".format(temperature2)
            log_message += (
                " - Humidity: {:.1f} %".format(humidity2) if humidity2 is not None else ""
            )
            log_message += (
                " - Pressure: {:.1f} hPa".format(pressure2)
                if pressure2 is not None
                else ""
            )
            logging.debug(log_message)

            last_updated2 = last_changed2

        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice["/UpdateIndex"] + 1  # increment index
        if index > 255:  # maximum value of the index
            index = 0  # overflow from 255 to 0
        self._dbusservice["/UpdateIndex"] = index
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change


class DbusMqttTemperatureService3:
    def __init__(
        self,
        servicename,
        deviceinstance,
        paths,
        productname="MQTT Temperature 3",
        customname="MQTT Temperature 3",
        connection="MQTT Temperature service 3",
    ):
        self._dbusservice = VeDbusService(servicename,dbusconnection())
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path("/Mgmt/ProcessName", __file__)
        self._dbusservice.add_path(
            "/Mgmt/ProcessVersion",
            "Unkown version, and running on Python " + platform.python_version(),
        )
        self._dbusservice.add_path("/Mgmt/Connection", connection)

        # Create the mandatory objects
        self._dbusservice.add_path("/DeviceInstance", deviceinstance)
        self._dbusservice.add_path("/ProductId", 0xFFFF)
        self._dbusservice.add_path("/ProductName", productname)
        self._dbusservice.add_path("/CustomName", customname)
        self._dbusservice.add_path("/FirmwareVersion", "0.0.1 (20230823)")
        # self._dbusservice.add_path('/HardwareVersion', '')
        self._dbusservice.add_path("/Connected", 1)

        self._dbusservice.add_path("/Status", 0)
        self._dbusservice.add_path("/TemperatureType", type3)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path,
                settings["initial"],
                gettextcallback=settings["textformat"],
                writeable=True,
                onchangecallback=self._handlechangedvalue,
            )

        GLib.timeout_add(1000, self._update)  # pause 1000ms before the next request

    def _update(self):
        global last_changed3, last_updated3

        now = int(time())

        if last_changed3 != last_updated3:
            self._dbusservice["/Temperature"] = (
                round(temperature3, 2) if temperature3 is not None else None
            )
            self._dbusservice["/Humidity"] = (
                round(humidity3, 2) if humidity3 is not None else None
            )
            self._dbusservice["/Pressure"] = (
                round(pressure3, 0) if pressure3 is not None else None
            )

            log_message = "Temperature: {:.1f} °C".format(temperature3)
            log_message += (
                " - Humidity: {:.1f} %".format(humidity3) if humidity3 is not None else ""
            )
            log_message += (
                " - Pressure: {:.1f} hPa".format(pressure3)
                if pressure3 is not None
                else ""
            )
            logging.debug(log_message)

            last_updated3 = last_changed3

        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice["/UpdateIndex"] + 1  # increment index
        if index > 255:  # maximum value of the index
            index = 0  # overflow from 255 to 0
        self._dbusservice["/UpdateIndex"] = index
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change


class DbusMqttTemperatureService4:
    def __init__(
        self,
        servicename,
        deviceinstance,
        paths,
        productname="MQTT Temperature 4",
        customname="MQTT Temperature 4",
        connection="MQTT Temperature service 4",
    ):
        self._dbusservice = VeDbusService(servicename,dbusconnection())
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path("/Mgmt/ProcessName", __file__)
        self._dbusservice.add_path(
            "/Mgmt/ProcessVersion",
            "Unkown version, and running on Python " + platform.python_version(),
        )
        self._dbusservice.add_path("/Mgmt/Connection", connection)

        # Create the mandatory objects
        self._dbusservice.add_path("/DeviceInstance", deviceinstance)
        self._dbusservice.add_path("/ProductId", 0xFFFF)
        self._dbusservice.add_path("/ProductName", productname)
        self._dbusservice.add_path("/CustomName", customname)
        self._dbusservice.add_path("/FirmwareVersion", "0.0.1 (20230823)")
        # self._dbusservice.add_path('/HardwareVersion', '')
        self._dbusservice.add_path("/Connected", 1)

        self._dbusservice.add_path("/Status", 0)
        self._dbusservice.add_path("/TemperatureType", type4)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path,
                settings["initial"],
                gettextcallback=settings["textformat"],
                writeable=True,
                onchangecallback=self._handlechangedvalue,
            )

        GLib.timeout_add(1000, self._update)  # pause 1000ms before the next request

    def _update(self):
        global last_changed4, last_updated4

        now = int(time())

        if last_changed4 != last_updated4:
            self._dbusservice["/Temperature"] = (
                round(temperature4, 2) if temperature4 is not None else None
            )
            self._dbusservice["/Humidity"] = (
                round(humidity4, 2) if humidity4 is not None else None
            )
            self._dbusservice["/Pressure"] = (
                round(pressure4, 0) if pressure4 is not None else None
            )

            log_message = "Temperature: {:.1f} °C".format(temperature4)
            log_message += (
                " - Humidity: {:.1f} %".format(humidity4) if humidity4 is not None else ""
            )
            log_message += (
                " - Pressure: {:.1f} hPa".format(pressure4)
                if pressure4 is not None
                else ""
            )
            logging.debug(log_message)

            last_updated4 = last_changed4

        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice["/UpdateIndex"] + 1  # increment index
        if index > 255:  # maximum value of the index
            index = 0  # overflow from 255 to 0
        self._dbusservice["/UpdateIndex"] = index
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change        


class DbusMqttTemperatureService5:
    def __init__(
        self,
        servicename,
        deviceinstance,
        paths,
        productname="MQTT Temperature 5",
        customname="MQTT Temperature 5",
        connection="MQTT Temperature service 5",
    ):
        self._dbusservice = VeDbusService(servicename,dbusconnection())
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path("/Mgmt/ProcessName", __file__)
        self._dbusservice.add_path(
            "/Mgmt/ProcessVersion",
            "Unkown version, and running on Python " + platform.python_version(),
        )
        self._dbusservice.add_path("/Mgmt/Connection", connection)

        # Create the mandatory objects
        self._dbusservice.add_path("/DeviceInstance", deviceinstance)
        self._dbusservice.add_path("/ProductId", 0xFFFF)
        self._dbusservice.add_path("/ProductName", productname)
        self._dbusservice.add_path("/CustomName", customname)
        self._dbusservice.add_path("/FirmwareVersion", "0.0.1 (20230823)")
        # self._dbusservice.add_path('/HardwareVersion', '')
        self._dbusservice.add_path("/Connected", 1)

        self._dbusservice.add_path("/Status", 0)
        self._dbusservice.add_path("/TemperatureType", type5)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path,
                settings["initial"],
                gettextcallback=settings["textformat"],
                writeable=True,
                onchangecallback=self._handlechangedvalue,
            )

        GLib.timeout_add(1000, self._update)  # pause 1000ms before the next request

    def _update(self):
        global last_changed5, last_updated5

        now = int(time())

        if last_changed5 != last_updated5:
            self._dbusservice["/Temperature"] = (
                round(temperature5, 2) if temperature5 is not None else None
            )
            self._dbusservice["/Humidity"] = (
                round(humidity5, 2) if humidity5 is not None else None
            )
            self._dbusservice["/Pressure"] = (
                round(pressure5, 0) if pressure5 is not None else None
            )

            log_message = "Temperature: {:.1f} °C".format(temperature5)
            log_message += (
                " - Humidity: {:.1f} %".format(humidity5) if humidity5 is not None else ""
            )
            log_message += (
                " - Pressure: {:.1f} hPa".format(pressure5)
                if pressure5 is not None
                else ""
            )
            logging.debug(log_message)

            last_updated5 = last_changed5

        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice["/UpdateIndex"] + 1  # increment index
        if index > 255:  # maximum value of the index
            index = 0  # overflow from 255 to 0
        self._dbusservice["/UpdateIndex"] = index
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change
        
def main():
    _thread.daemon = True  # allow the program to quit

    from dbus.mainloop.glib import (  # pyright: ignore[reportMissingImports]
        DBusGMainLoop,
    )

    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)

    # MQTT setup
    client = mqtt.Client("MqttTemperature_" + str(config["MQTT"]["device_instance"]))
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    client.on_message = on_message

    # check tls and use settings, if provided
    if "tls_enabled" in config["MQTT"] and config["MQTT"]["tls_enabled"] == "1":
        logging.info("MQTT client: TLS is enabled")

        if (
            "tls_path_to_ca" in config["MQTT"]
            and config["MQTT"]["tls_path_to_ca"] != ""
        ):
            logging.info(
                'MQTT client: TLS: custom ca "%s" used'
                % config["MQTT"]["tls_path_to_ca"]
            )
            client.tls_set(config["MQTT"]["tls_path_to_ca"], tls_version=2)
        else:
            client.tls_set(tls_version=2)

        if "tls_insecure" in config["MQTT"] and config["MQTT"]["tls_insecure"] != "":
            logging.info(
                "MQTT client: TLS certificate server hostname verification disabled"
            )
            client.tls_insecure_set(True)

    # check if username and password are set
    if (
        "username" in config["MQTT"]
        and "password" in config["MQTT"]
        and config["MQTT"]["username"] != ""
        and config["MQTT"]["password"] != ""
    ):
        logging.info(
            'MQTT client: Using username "%s" and password to connect'
            % config["MQTT"]["username"]
        )
        client.username_pw_set(
            username=config["MQTT"]["username"], password=config["MQTT"]["password"]
        )

    # connect to broker
    logging.info(
        f"MQTT client: Connecting to broker {config['MQTT']['broker_address']} on port {config['MQTT']['broker_port']}"
    )
    client.connect(
        host=config["MQTT"]["broker_address"], port=int(config["MQTT"]["broker_port"])
    )
    client.loop_start()

    # wait to receive first data, else the JSON is empty and phase setup won't work
    i = 0
    while temperature == -999:
        if i % 12 != 0 or i == 0:
            logging.info("Waiting 5 seconds for receiving first data...")
        else:
            logging.warning(
                "Waiting since %s seconds for receiving first data..." % str(i * 5)
            )
        sleep(5)
        i += 1

    # formatting
    def _celsius(p, v):
        return str("%.2f" % v) + "°C"

    def _percent(p, v):
        return str("%.1f" % v) + "%"

    def _pressure(p, v):
        return str("%i" % v) + "hPa"

    def _n(p, v):
        return str("%i" % v)

    paths_dbus = {
        "/Temperature": {"initial": None, "textformat": _celsius},
        "/Humidity": {"initial": None, "textformat": _percent},
        "/Pressure": {"initial": None, "textformat": _pressure},
        "/UpdateIndex": {"initial": 0, "textformat": _n},
    }

    DbusMqttTemperatureService(
        servicename="com.victronenergy.temperature.mqtt_temperature_"
        + str(config["MQTT"]["device_instance"]),
        deviceinstance=int(config["MQTT"]["device_instance"]),
        customname=config["MQTT"]["device_name"],
        paths=paths_dbus,
    )


    if int(config["DEFAULT"]["instances"]) > 1 :
        logging.info("Create Instance 2")
        DbusMqttTemperatureService2(
            servicename="com.victronenergy.temperature.mqtt_temperature_"
            + str(config["MQTT"]["device_instance2"]),
            deviceinstance=int(config["MQTT"]["device_instance2"]),
            customname=config["MQTT"]["device_name2"],
            paths=paths_dbus,
        )

    if int(config["DEFAULT"]["instances"]) > 2 :
        logging.info("Create Instance 3")
        DbusMqttTemperatureService3(
            servicename="com.victronenergy.temperature.mqtt_temperature_"
            + str(config["MQTT"]["device_instance3"]),
            deviceinstance=int(config["MQTT"]["device_instance3"]),
            customname=config["MQTT"]["device_name3"],
            paths=paths_dbus,
        )
        
    if int(config["DEFAULT"]["instances"]) > 3 :
        logging.info("Create Instance 4")
        DbusMqttTemperatureService4(
            servicename="com.victronenergy.temperature.mqtt_temperature_"
            + str(config["MQTT"]["device_instance4"]),
            deviceinstance=int(config["MQTT"]["device_instance4"]),
            customname=config["MQTT"]["device_name4"],
            paths=paths_dbus,
        )

    if int(config["DEFAULT"]["instances"]) > 4 :
        logging.info("Create Instance 5")
        DbusMqttTemperatureService5(
            servicename="com.victronenergy.temperature.mqtt_temperature_"
            + str(config["MQTT"]["device_instance5"]),
            deviceinstance=int(config["MQTT"]["device_instance5"]),
            customname=config["MQTT"]["device_name5"],
            paths=paths_dbus,
        )    
    
    logging.info(
        "Connected to dbus and switching over to GLib.MainLoop() (= event based)"
    )
    mainloop = GLib.MainLoop()
    mainloop.run()


if __name__ == "__main__":
    main()
