#!/usr/bin/env python3

from pyrehau_neasmart import RehauNeaSmart
import paho.mqtt.client as mqtt
import time
from dotenv import load_dotenv
import os
from threading import Thread
import logging

load_dotenv()

REHAU_HOST = os.getenv('REHAU_HOST')
MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_PREFIX = os.getenv('MQTT_PREFIX')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

heatarea_modes = {
    0: "auto",
    1: "heat",
    2: "off"
}

logging.basicConfig(level=LOGLEVEL)


class Subscribe(Thread):
    """Thread charge pour consommer"""

    def __init__(self, mqtt, rehau):
        Thread.__init__(self)
        self.mqtt = mqtt
        self.rehau = rehau

    def run(self):
        """Code ran"""
        logging.info('Subscribe thread launched')
        topic = MQTT_PREFIX + '/+/+/set'
        self.mqtt.subscribe(topic)
        self.mqtt.loop_start()


class Publish(Thread):
    """Thread charge pour consommer"""

    def __init__(self, mqtt, rehau):
        Thread.__init__(self)
        self.mqtt = mqtt
        self.rehau = rehau

    def run(self):
        """Code ran"""
        logging.info('Publish thread launched')
        self.mqtt.loop_start()
        while True:
            for ha in self.rehau.heatareas():
                status = ha.status
                heatarea_name = status['heatarea_name']
                for item in status:
                    topic = MQTT_PREFIX + '/' + heatarea_name + '/' + item
                    if(item == 'heatarea_mode'):
                        value = heatarea_modes[int(status[item])]
                    else:
                        value = status[item]

                    # print("Publish %s / %s" % (topic, value))
                    self.mqtt.publish(topic, value, qos=1, retain=True)
            print('Sleeping for 5 seconds')
            time.sleep(5)


# The callback for when the client receives a CONNACK response from the server.
def mqtt_on_connect(client, userdata, flags, rc):
    if(rc == 0):
        logging.info("Connected to broker")
    else:
        logging.info("Connection failed")


# The callback for when a PUBLISH message is received from the server.
def mqtt_on_message(client, userdata, msg):
    logging.info(msg.topic+" "+str(msg.payload))


def mqtt_on_publish(client, userdata, result):
    logging.info("publish %s %s" % (client, userdata))


def mqtt_on_subscribe(client, obj, mid, granted_qos):
    logging.info("Subscribed: " + str(mid) + " " + str(granted_qos))


# MQTT PART
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = mqtt_on_connect
client.on_message = mqtt_on_message
client.on_publish = mqtt_on_publish
client.on_subscribe = mqtt_on_subscribe

# REHAU PART
rehau = RehauNeaSmart(REHAU_HOST)

subcribe = Subscribe(client, rehau)
publish = Publish(client, rehau)

# Lancement des threads
subcribe.start()
publish.start()

# Attend que les threads se terminent
subcribe.join()
publish.join()
