#!/usr/bin/python3.11

import os
import time
import logging
import json
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
DHT_RETRY_INTERVAL = float(os.environ.get("DHT_RETRY_INTERVAL"))
MQTT_RECONNECT_INTERVAL = float(os.environ.get("MQTT_RECONNECT_INTERVAL"))

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
        return on_connect_fail()

    periodically_publish_dht22_data(mqtt_client)
    mqtt_client.loop_forever(timeout=15, retry_first_connection=True)


def on_connect(
    client: mqtt.Client,
    userdata: Any,
    flags: Dict,
    reason_code: mqtt.ReasonCodes,
    properties: mqtt.Properties,
):
    if reason_code == 0:
        logging.info(f"Connected to MQTT broker at {BROKER_ADDRESS}")
    else:
        logging.error(f"Failed to connect, reason code: {reason_code}")


def on_connect_fail(
    client: mqtt.Client,
    userdata: Any,
    disconnect_flags: Dict,
    reason_code: mqtt.ReasonCodes,
    properties: mqtt.Properties,
):
    logging.warning(f"Connect failed with reason code: {reason_code}")
    logging.info(f"Retrying connection in {MQTT_RECONNECT_INTERVAL} seconds...")
    time.sleep(MQTT_RECONNECT_INTERVAL)
    client.reconnect()


def on_disconnect(
    client: mqtt.Client,
    userdata: Any,
    flags: Dict,
    reason_code: mqtt.ReasonCodes,
    properties: mqtt.Properties,
):
    logging.warning(f"Disconnected from MQTT broker, reason code: {reason_code}")
    logging.info(f"Retrying connection in {MQTT_RECONNECT_INTERVAL} seconds...")
    time.sleep(MQTT_RECONNECT_INTERVAL)
    client.reconnect()


def on_publish(
    client: mqtt.Client,
    userdata: Any,
    mid: int,
    reason_code: mqtt.ReasonCodes,
    properties: mqtt.Properties,
):
    logging.debug(f"Message published, reason code: {reason_code}")


def periodically_publish_dht22_data(client: mqtt.Client):
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
            logging.info(f"Retrying in {DHT_RETRY_INTERVAL} seconds...")
            time.sleep(DHT_RETRY_INTERVAL)
            continue

        time.sleep(PUBLISH_INTERVAL)


if __name__ == "__main__":
    main()
