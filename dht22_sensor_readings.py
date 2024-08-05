#!/usr/bin/python3

import logging
import adafruit_dht
from board import D17

dht_device = adafruit_dht.DHT22(D17)


def fetch_humidity():
    try:
        humidity = dht_device.humidity
        return humidity
    except Exception as e:
        logging.error(e)
        raise e


def fetch_temperature():
    try:
        temperature = dht_device.temperature
        return temperature
    except Exception as e:
        logging.error(e)
        raise e
