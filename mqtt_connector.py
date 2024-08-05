#!/usr/bin/python3

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
BROKER_PORT = os.environ.get("BROKER_PORT")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_USER = os.environ.get("CLIENT_USER")
CLIENT_PSSWD = os.environ.get("CLIENT_PSSWD")
PUBLISH_INTERVAL = float(os.environ.get("PUBLISH_INTERVAL"))

def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    mqtt_client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=False
    )
    mqtt_client.enable_logger()

    mqtt_client.username_pw_set(CLIENT_USER, CLIENT_PSSWD)
    mqtt_client.max_queued_messages_set(0)
    mqtt_client.connect(BROKER_ADDRESS, int(BROKER_PORT))
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_publish = on_publish
    periodically_publish_dht22_data(mqtt_client)
    mqtt_client.loop_forever()
    unacked_publish = set()


def on_connect(client, userdata, flags, reason_code, properties):
    if flags.session_present:
        logging.debug("Client connected with flags: {}".format(flags))
    if reason_code == 0:
        logging.debug(
            "{}  MQTT Client Connected to {}  {}".format(
                "#" * 30, BROKER_ADDRESS, "#" * 30
            )
        )
    if reason_code == "Client identifier not valid":
        logging.debug("Client return code: {}".format(reason_code))
    if reason_code == "Unsupported protocol version":
        logging.debug("Client return code: {}".format(reason_code))


def on_disconnect(client, userdata, flags, reason_code, properties):
    logging.warning("MQTT Client Disconnecting...")
    if reason_code == 0:
        logging.info("Success disconnect")
        # success disconnect
    if reason_code > 0:
        logging.info(reason_code)
        
def on_publish(client, userdata, mid, reason_codes, properties):
    logging.debug(reason_codes)
def periodically_publish_dht22_data(client: mqtt.Client) -> None:
    while True:
        try:
            dts = datetime.now()
            res = {
                "temperature": dht22.fetch_temperature(),
                "humidity": dht22.fetch_humidity(),
                "dts": dts.strftime("%d/%m/%Y %H:%M:%S"),
            }                
            client.publish("sensor/{}/temperature/state".format(CLIENT_ID), json.dumps(res["temperature"]))
            client.publish("sensor/{}/humidity/state".format(CLIENT_ID), json.dumps(res["humidity"]))
            client.publish("sensor/{}/timestamp/state".format(CLIENT_ID), json.dumps(res["dts"]))
            time.sleep(PUBLISH_INTERVAL)
        except Exception as e:
            logging.error(e)
            continue


if __name__ == "__main__":
    main()
