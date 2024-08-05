#!/usr/bin/python3.11

import os
import time
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Any, Dict
import paho.mqtt.client as mqtt
import dht22_sensor_readings as dht22

load_dotenv()
BROKER_ADDRESS = os.environ.get("BROKER_ADDRESS")
BROKER_PORT = int(os.environ.get("BROKER_PORT"))
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_USER = os.environ.get("CLIENT_USER")
CLIENT_PSSWD = os.environ.get("CLIENT_PSSWD")
PUBLISH_INTERVAL = float(os.environ.get("PUBLISH_INTERVAL"))

RETRY_INTERVAL = 2

TOPIC_TEMPERATURE = f"sensor/{CLIENT_ID}/temperature/state"
TOPIC_HUMIDITY = f"sensor/{CLIENT_ID}/humidity/state"


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    mqtt_client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=False
    )
    # mqtt_client.enable_logger()

    mqtt_client.username_pw_set(CLIENT_USER, CLIENT_PSSWD)
    mqtt_client.max_queued_messages_set(0)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_connect_fail = on_connect_fail
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_publish = on_publish

    try:
        mqtt_client.connect(BROKER_ADDRESS, (BROKER_PORT))
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {e}")
        return

    periodically_publish_dht22_data(mqtt_client)
    mqtt_client.loop_forever(timeout=15, retry_first_connection=True)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logging.info(f"Connected to MQTT broker at {BROKER_ADDRESS}")
    else:
        logging.error(f"Failed to connect, reason code: {reason_code}")


def on_connect_fail(client, userdata, disconnect_flags, reason_code, properties):
    logging.warning(f"Connect failed with reason code: {reason_code}")


def on_disconnect(client, userdata, flags, reason_code, properties):
    logging.warning(f"Disconnected from MQTT broker, reason code: {reason_code}")


def on_publish(client, userdata, mid, reason_codes, properties):
    logging.debug(f"Message published, reason code: {reason_codes}")


def periodically_publish_dht22_data(client: mqtt.Client) -> None:
    while True:
        try:
            res = {
                "temperature": dht22.fetch_temperature(),
                "humidity": dht22.fetch_humidity(),
            }
            client.publish(TOPIC_TEMPERATURE, json.dumps(res["temperature"]))
            client.publish(TOPIC_HUMIDITY, json.dumps(res["humidity"]))
            logging.debug(json.dumps(res))
        except Exception as e:
            logging.error(f"Error reading sensor data: {e}")
            logging.info(f"Retrying in {RETRY_INTERVAL} seconds...")
            time.sleep(RETRY_INTERVAL)
            continue

        time.sleep(PUBLISH_INTERVAL)


if __name__ == "__main__":
    main()
