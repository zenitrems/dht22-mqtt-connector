FROM python:3.11.4-alpine

RUN apk update && apk upgrade
RUN apk add git libgpiod build-base
RUN addgroup dht && adduser -D -G dht dht
USER dht
WORKDIR /home/dht

RUN git clone https://github.com/zenitrems/dht22-mqtt-connector.git

WORKDIR /home/dht/dht22-mqtt-connector

RUN python3 -m venv .venv && . .venv/bin/activate

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3", "mqtt_connector.py"]