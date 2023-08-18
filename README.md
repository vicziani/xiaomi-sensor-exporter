# Xiaomi Sensor Exporter

This Python web application connect to Xiaomi Mi Temperature and Humidity Monitor 2 (LYWSD03MMC)
sensors, get the temperature, humidity and battery values, and exports it 
in [OpenMetrics](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md) format.
Prometheus scraper can interpret this format.

Because of `bluepy` (Bluetooth LE on Linux) dependency it works only on Linux.
Recommended platform is Raspberry PI.

## Configuration file

Scan the Bluetooth devices with the following command:

```shell
sudo hcitool lescan
```

The output will be something like this:

```plain
61-0D-49-18-9F-C8 (unknown)
49-49-73-D6-F3-47 (unknown)
24-48-8C-94-96-4C (unknown)
24-48-8C-94-96-4C LYWSD03MMC
C8-6A-2F-5E-10-22 (unknown)
98-87-5C-C1-DC-5E MI_SCALE
```

Find the MAC address next to `LYWSD03MMC` string.

Create a `config.yaml` configuration file:

```
port: 9093
devices:
  - name: workroom
    address: 24-48-8C-94-96-4C
```

## Run

```shell
git clone https://github.com/vicziani/xiaomi-sensor-exporter
python -m venv venv
venv/bin/activate
pip install -r requirements.txt
python xiaomi_sensor_exporter.py -c config.yaml
```

## Run in Docker

Create a configuration file for example at the `/home/pi/xiaomi_sensor_exporter/config.yaml` location.

Run the container with the following command:

```shell
docker run -v /home/pi/xiaomi_sensor_exporter/config.yaml:/app/config/config.yaml --net=host --privileged --name xiaomi -d vicziani/xiaomi-sensor-exporter:0.0.1
```

Unfortunately I didn't find any solution to run the command without `--net=host --privileged` parameters. They are necessary to access the host's Bluetooth stack.

## Usage

The main page is `http://raspberrypi:9093`.

The metrics page is `http://raspberrypi:9093/metrics`.

You will get something like this:

```plain
#HELP xiaomi_sensor_exporter_number_of_sensors Number of sensors
#TYPE xiaomi_sensor_exporter_number_of_sensors gauge
xiaomi_sensor_exporter_number_of_sensors 1
#HELP xiaomi_sensor_exporter_temperature_celsius Temperature
#TYPE xiaomi_sensor_exporter_temperature_celsius gauge
xiaomi_sensor_exporter_temperature_celsius{name="workroom",address="24-48-8C-94-96-4C"} 26.26
#HELP xiaomi_sensor_exporter_humidity_percent Humidity
#TYPE xiaomi_sensor_exporter_humidity_percent gauge
xiaomi_sensor_exporter_humidity_percent{name="workroom",address="24-48-8C-94-96-4C"} 65
#HELP xiaomi_sensor_exporter_battery_volt Battery
#TYPE xiaomi_sensor_exporter_battery_volt Volt
xiaomi_sensor_exporter_battery_volt{name="workroom",address="24-48-8C-94-96-4C"} 3.102
```