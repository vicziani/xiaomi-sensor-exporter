import argparse
import sys
from functools import partial
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import yaml
from yaml.parser import ParserError
from yaml.loader import SafeLoader
from bluepy import btle

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]",
        description="Prometheus exporter for Xiaomi sensors"
    )
    parser.add_argument(
        "-c", "--config", help="path to config file")

    return parser

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.data = {}

    def handleNotification(self, cHandle, data):
        databytes = bytearray(data)
        temperature = int.from_bytes(databytes[0:2],"little") / 100
        humidity = int.from_bytes(databytes[2:3],"little")
        battery = int.from_bytes(databytes[3:5],"little") / 1000
        print(f"Temperature: {temperature}, humidity: {humidity}, battery: {battery}")
        self.data = {"temperature": temperature, "humidity": humidity, "battery": battery, "success": True}

def read_values(mac):
    print(f"Connecting to {mac}")
    connected = False
    try:
        # Timeout not released: https://github.com/IanHarvey/bluepy/pull/374
        dev = btle.Peripheral(mac)
        connected = True
        print("Connection done...")
        delegate = MyDelegate()
        dev.setDelegate(delegate)
        print("Waiting for data...")
        dev.waitForNotifications(15.0)
        return delegate.data
    except btle.BTLEDisconnectError as error:
        print(error)
        return {"success": False}
    finally:
        if connected:
            dev.disconnect()

def to_measures(device):
    response = f"""#HELP xiaomi_sensor_exporter_temperature_celsius Temperature
#TYPE xiaomi_sensor_exporter_temperature_celsius gauge
xiaomi_sensor_exporter_temperature_celsius{{name="{device["name"]}",address="{device["address"]}"}} {device["data"]["temperature"]}
#HELP xiaomi_sensor_exporter_humidity_percent Humidity
#TYPE xiaomi_sensor_exporter_humidity_percent gauge
xiaomi_sensor_exporter_humidity_percent{{name="{device["name"]}",address="{device["address"]}"}} {device["data"]["humidity"]}
#HELP xiaomi_sensor_exporter_battery_volt Battery
#TYPE xiaomi_sensor_exporter_battery_volt Volt
xiaomi_sensor_exporter_battery_volt{{name="{device["name"]}",address="{device["address"]}"}} {device["data"]["battery"]}
"""
    return response

class WebRequestHandler(BaseHTTPRequestHandler):

    # https://stackoverflow.com/a/52046062
    def __init__(self, devices, *args, **kwargs):
        self.devices = devices
        # BaseHTTPRequestHandler calls do_GET **inside** __init__ !!!
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/":
            return self.get_index()
        elif self.path == "/metrics":
            return self.get_metrics()
        else:
            return self.get_not_found()

    def get_index(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.1; charset=utf-8")
        self.end_headers()
        self.wfile.write(str(self.devices).encode("utf-8"))

    def get_metrics(self):
        response = f"""#HELP xiaomi_sensor_exporter_number_of_sensors Number of sensors
#TYPE xiaomi_sensor_exporter_number_of_sensors gauge
xiaomi_sensor_exporter_number_of_sensors {len(devices)}"""

        for device in devices:
            device["data"] = read_values(device["address"])
            if device["data"]["success"] is True:
                response += to_measures(device)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.1; charset=utf-8")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

    def get_not_found(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; version=0.0.1; charset=utf-8")
        self.end_headers()
        self.wfile.write("Not found".encode("utf-8"))

if __name__ == "__main__":
    devices = []
    port = 9093

    parser = init_argparse()
    args = parser.parse_args()

    devices_config_file = args.config

    if devices_config_file:
        try:
            with open(devices_config_file, encoding="utf-8") as f:
                data = yaml.load(f, SafeLoader)
                if "port" in data:
                    port = data["port"]
                if "devices" in data:
                    devices = data["devices"]
        except FileNotFoundError:
            print(f"Configuration file not found: {devices_config_file}")
            sys.exit(-1)
        except ParserError:
            print(f"Invalid configuration file: {devices_config_file}")
            sys.exit(-1)


    print(f"Creating xiaomi_sensor_exporter server on port {port}")
    handler = partial(WebRequestHandler, devices)
    server = HTTPServer(("0.0.0.0", port), handler)
    server.serve_forever()
