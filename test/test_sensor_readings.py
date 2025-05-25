#!/usr/bin/python3

import sys
import os
import time

sys.path.append(os.getcwd())

import bme280_sensor_readings as bme280  # nombre correcto del módulo

def fetch_readings_every_2_seconds():
    while True:
        try:
            data = bme280.get_sensor_data()
            print("Temperature: {}°C, Humidity: {}%, Pressure: {} hPa".format(
                data["temperature"],
                data["humidity"],
                data["pressure"]
            ))
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    fetch_readings_every_2_seconds()
