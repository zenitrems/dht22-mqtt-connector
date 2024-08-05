#!/usr/bin/python3

import logging
import board
import adafruit_dht

dht_device = adafruit_dht.DHT22(board.D17, use_pulseio=False)


def fetch_humidity():
    try:
        humidity = dht_device.humidity
        return humidity
    except Exception as error:
        dht_device.exit()
        logging.error(error)
        raise error


def fetch_temperature():
    try:
        temperature = dht_device.temperature
        return temperature
    except Exception as error:
        dht_device.exit()
        logging.error(error)
        raise error
