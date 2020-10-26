#!/usr/bin/env python3

from pyrehau_neasmart import RehauNeaSmart
import paho.mqtt.client as mqtt
import time
from dotenv import load_dotenv
import os
import sys

import threading

import logging

load_dotenv()

REHAU_HOST = os.getenv("REHAU_HOST")
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_PREFIX = os.getenv("MQTT_PREFIX")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")
LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
REHAU_CHECK_INTERVAL = os.getenv("REHAU_CHECK_INTERVAL")

heatarea_modes = {0: "auto", 1: "heat", 2: "off"}
subscribe_topic_pattern = MQTT_PREFIX + "/+/+/set"

logging.basicConfig(level=LOGLEVEL)


class Subscribe(threading.Thread):
    """Thread charge pour consommer"""

    def __init__(self, mqtt, rehau):
        threading.Thread.__init__(self)
        self.mqtt = mqtt
        self.rehau = rehau

    def run(self):
        """Code ran"""
        logging.info("Subscribe thread launched")
        self.mqtt.subscribe(subscribe_topic_pattern)


class Publish(threading.Thread):
    """Thread charge pour consommer"""

    def __init__(self, mqtt, rehau):
        threading.Thread.__init__(self)
        self.mqtt = mqtt
        self.rehau = rehau

    def run(self):
        """Code ran"""
        logging.info("Publish thread launched")
        while True:
            try:
                heatareas = self.rehau.heatareas()
            except:
                logging.error("error timeout")
                heatareas = False

            if heatareas:
                for ha in heatareas:
                    try:
                        status = ha.status
                        heatarea_name = status["heatarea_name"]
                        logging.info("Publishing for %s" % heatarea_name)
                        for item in status:
                            topic = MQTT_PREFIX + "/" + heatarea_name + "/" + item
                            if item == "heatarea_mode":
                                value = heatarea_modes[int(status[item])]
                            else:
                                value = status[item]

                            # print("Publish %s / %s" % (topic, value))
                            self.mqtt.publish(topic, value, qos=1, retain=True)
                    except:
                        logging.error("another timeout")

            print("Sleeping for %s seconds" % REHAU_CHECK_INTERVAL)
            time.sleep(int(REHAU_CHECK_INTERVAL))


# The callback for when the client receives a CONNACK response from the server.
def mqtt_on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to broker")
    else:
        logging.info("Connection failed")


# The callback for when a PUBLISH message is received from the server.
def mqtt_on_message(client, userdata, msg):
    logging.info(msg.topic + " " + str(msg.payload))


def mqtt_on_publish(client, userdata, result):
    logging.debug("publish %s %s %s" % (client, userdata, result))


def mqtt_on_subscribe(client, obj, mid, granted_qos):
    logging.info("Subscribed: " + str(mid) + " " + str(granted_qos))


# MQTT PART
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = mqtt_on_connect
client.on_message = mqtt_on_message
client.on_publish = mqtt_on_publish
client.on_subscribe = mqtt_on_subscribe

client.connect(MQTT_HOST, MQTT_PORT)

# REHAU PART
rehau = RehauNeaSmart(REHAU_HOST)

subcribe = Subscribe(client, rehau)
publish = Publish(client, rehau)

try:
    # Lancement des threads
    subcribe.start()
    publish.start()

    client.loop_forever()
    client.loop_forever()
except KeyboardInterrupt:
    print("Ctrl+C pressed...")
    sys.exit(0)
