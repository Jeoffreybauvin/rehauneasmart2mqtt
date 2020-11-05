#!/usr/bin/env python3
# Readme needed

from pyrehau_neasmart import RehauNeaSmart
import paho.mqtt.client as mqtt
import time
from dotenv import load_dotenv
import os
import re
import sys

import threading

import logging

load_dotenv()

NAME = "rehauneasmart2mqtt"

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

log = logging.getLogger(NAME)
log.setLevel(LOGLEVEL)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)


# to do : republish after setting new state
def set_rehau_cmd(topic, msg):
    # topic format : rehau/Bureau/t_target/set
    regex_topic = re.search(MQTT_PREFIX + "\/(\S*)\/(\S*)\/set", topic)
    if regex_topic:
        topic_ha_name = regex_topic.group(1)
        topic_action_name = regex_topic.group(2)
    else:
        log.error("[Subscribe] Error while extracting heatarea name and action")

    # Because msg is bytes
    msg = msg.decode("UTF-8")

    heatareas = rehau.heatareas()
    if heatareas:
        for ha in heatareas:
            # Handle timeouts in pyrehau_neasmart
            try:
                status = ha.status
                heatarea_name = status["heatarea_name"]
                if heatarea_name == topic_ha_name:

                    if topic_action_name == "t_target":
                        ha.set_t_target(msg)
                    elif topic_action_name == "heatarea_mode":
                        log.error(heatarea_modes)
                        for ha_modes in heatarea_modes:
                            if heatarea_modes[ha_modes] == msg:
                                right_heatarea_mode = ha_modes
                                break
                        ha.set_heatarea_mode(right_heatarea_mode)
                    else:
                        log.error(
                            "[Subscribe] This actions %s is unknown" % topic_action_name
                        )
            except:
                log.error("[Subscribe] Something went wrong while talking to Rehau")


class Subscribe(threading.Thread):
    """Thread charge pour consommer"""

    def __init__(self, mqtt, rehau):
        threading.Thread.__init__(self)
        self.mqtt = mqtt
        self.rehau = rehau

    def run(self):
        """Code ran"""
        log.info(
            "Subscribe thread launched, subscribing to %s" % subscribe_topic_pattern
        )
        self.mqtt.subscribe(subscribe_topic_pattern)


class Publish(threading.Thread):
    """Thread charge pour consommer"""

    def __init__(self, mqtt, rehau):
        threading.Thread.__init__(self)
        self.mqtt = mqtt
        self.rehau = rehau

    def run(self):
        """Code ran"""
        log.info("Publish thread launched")
        while True:
            # Handle timeouts in pyrehau_neasmart
            try:
                heatareas = self.rehau.heatareas()
            except:
                log.error("Timeout on Rehau")
                heatareas = False

            if heatareas:
                for ha in heatareas:
                    # Handle timeouts in pyrehau_neasmart
                    try:
                        status = ha.status
                        heatarea_name = status["heatarea_name"]
                        log.info("Publishing for heatarea %s" % heatarea_name)
                        for item in status:
                            topic = MQTT_PREFIX + "/" + heatarea_name + "/" + item
                            if item == "heatarea_mode":
                                value = heatarea_modes[int(status[item])]
                            else:
                                value = status[item]

                            # print("Publish %s / %s" % (topic, value))
                            self.mqtt.publish(topic, value, qos=1, retain=True)
                    except:
                        log.error("Another timeout on Rehau")

            log.info("Sleeping Publish thread for %s seconds" % REHAU_CHECK_INTERVAL)
            time.sleep(int(REHAU_CHECK_INTERVAL))


# The callback for when the client receives a CONNACK response from the server.
def mqtt_on_connect(client, userdata, flags, rc):
    if rc == 0:
        log.info("Connected to broker")
    else:
        log.info("Connection failed")


# The callback for when a PUBLISH message is received from the server.
def mqtt_on_message(client, userdata, msg):
    log.info(msg.topic + " " + str(msg.payload))
    set_rehau_cmd(msg.topic, msg.payload)


def mqtt_on_publish(client, userdata, result):
    log.debug("publish %s %s %s" % (client, userdata, result))


def mqtt_on_subscribe(client, obj, mid, granted_qos):
    log.info("Subscribed: " + str(mid) + " " + str(granted_qos))


log.info("Starting %s" % NAME)

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
