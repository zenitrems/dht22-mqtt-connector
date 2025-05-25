#!/usr/bin/python3.11

import smbus2
import bme280

def get_sensor_data():
    port = 1
    address = 0x76  #sudo i2cdetect -y 1
    bus = smbus2.SMBus(port)
    calibration_params = bme280.load_calibration_params(bus, address)
    data = bme280.sample(bus, address, calibration_params)
    return {
        'temperature': round(data.temperature, 2),
        'humidity': round(data.humidity, 2),
        'pressure': round(data.pressure, 2)
    }