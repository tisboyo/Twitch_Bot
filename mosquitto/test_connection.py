"""
##demo code provided by Steve Cope at www.steves-internet-guide.com
##email steve@steves-internet-guide.com
##Free to use for any purpose
##If you like and use this code you can
##buy me a drink here https://www.paypal.me/StepenCope

Passwords demo code
"""
import time
from os import getenv

import paho.mqtt.client as mqtt  # import the client1

QOS1 = 1
QOS2 = 1
CLEAN_SESSION = True
broker = getenv("WEB_HOSTNAME")
# broker_address="iot.eclipse.org"


def on_disconnect(client, userdata, flags, rc=0):
    m = "DisConnected flags" + "result code " + str(rc)
    print(m)


def on_connect(client, userdata, flags, rc):
    print("Connected flags ", str(flags), "result code ", str(rc))


def on_message(client, userdata, message):
    print("message received  ", str(message.payload.decode("utf-8")))


def on_publish(client, userdata, mid):
    print("message published ")  # , str(message.payload.decode("utf-8")))


print("creating client 1 with clean session set to", CLEAN_SESSION)
client1 = mqtt.Client("Python1", clean_session=CLEAN_SESSION)  # create new instance
# edit code for passwords
print("setting  password")
client1.username_pw_set(username="tisboyo", password="testpass")
##
client1.on_message = on_message  # attach function to callback
client1.on_connect = on_connect
print("connecting to ", broker)
# client1.tls_set(cert_reqs=ssl.CERT_NONE)
client1.tls_set()
client1.connect(broker, 8883)
client1.loop_start()
# client1.on_disconnect=on_disconnect
time.sleep(3)
# client1.loop()
client1.disconnect()
client1.loop_stop()

# print("Not sending username password")
# client1 = mqtt.Client("Python1", clean_session=CLEAN_SESSION)
# client1.on_message = on_message  # attach function to callback
# client1.on_connect = on_connect
# print("connecting to ", broker)
# client1.connect(broker)
# client1.loop_start()
# time.sleep(5)
# print("Disconnecting from ", broker)
# client1.disconnect()
# time.sleep(1)
# client1.loop_stop()
