# Xiaomi Sensor Exporter

This Python web application connect to Xiaomi Mi Temperature and Humidity Monitor 2 (LYWSD03MMC)
sensors, get the temperature, humidity and battery values, and exports it 
in [OpenMetrics](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md) format.
Prometheus scraper can interpret this format.

Because of `bluepy` (Bluetooth LE on Linux) dependency it works only on Linux.
Recommended platform is Raspberry PI.

Find the source code and full documentation at the [GitHub project](https://github.com/vicziani/xiaomi-sensor-exporter).