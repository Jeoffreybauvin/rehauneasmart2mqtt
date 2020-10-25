#!/usr/bin/env python3

from pyrehau_neasmart import RehauNeaSmart
import paho.mqtt.client as mqtt
import time
from dotenv import load_dotenv
import os

load_dotenv()

REHAU_HOST = os.getenv('REHAU_HOST')
MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_PREFIX = os.getenv('MQTT_PREFIX')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')

heatarea_modes = {
    0: "auto",
    1: "heat",
    2: "off"
}

rh = RehauNeaSmart(REHAU_HOST)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if(rc == 0):
        print("Connected to broker")
    else:
        print("Connection failed")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def on_publish(client, userdata, result):
    if not result:
        print('error while publishing')


def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe

client.connect(MQTT_HOST, MQTT_PORT, 60)

topic = MQTT_PREFIX + '/+/+/set'

client.subscribe(topic)

client.loop_forever()


# print('Starting the loop')
# try:
#     while True:
#         for ha in rh.heatareas():
#             status = ha.status
#             heatarea_name = status['heatarea_name']
#             for item in status:
#                 topic = MQTT_PREFIX + '/' + heatarea_name + '/' + item
#                 if(item == 'heatarea_mode'):
#                     value = heatarea_modes[int(status[item])]
#                 else:
#                     value = status[item]
#
#                 print("Publish %s / %s" % (topic, value))
#                 client.publish(topic, value, qos=1, retain=True)
#         print('Sleeping for 5 seconds')
#         time.sleep(30)
# except KeyboardInterrupt:
#     client.disconnect()
#     client.loop_stop()
