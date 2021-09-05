from os import getenv

from Adafruit_IO import Client as AIO_Client
from Adafruit_IO.errors import RequestError as RequestError
from paho.mqtt import client as mqtt


class AIO:
    def __init__(self, user=None, key=None):
        self.ADAFRUIT_IO_USERNAME = getenv("ADAFRUIT_IO_USER") or user
        self.ADAFRUIT_IO_KEY = getenv("ADAFRUIT_IO_KEY") or key
        self.__client = None
        self.AIO_CONNECTION_STATE = False

    def connect_to_aio(self):
        """Connect to Adafruit.IO"""
        # Create an instance of the REST client.
        if self.ADAFRUIT_IO_USERNAME is None or self.ADAFRUIT_IO_KEY is None:
            print("Adafruit IO keys not found, aborting connection")
            return False

        try:
            print("Atempting to connect to AIO as " + self.ADAFRUIT_IO_USERNAME)
            self.__client = AIO_Client(self.ADAFRUIT_IO_USERNAME, self.ADAFRUIT_IO_KEY)
            print("Connected to Adafruit.IO")
            self.AIO_CONNECTION_STATE = True
            return True

        except Exception as e:
            print("Failed to connect to AIO, disabling it")
            print(e)
            self.AIO_CONNECTION_STATE = False
            return False

    def send(self, feed, value=1):
        """Send to an AdafruitIO topic"""

        if self.AIO_CONNECTION_STATE is False:
            try:
                if not self.connect_to_aio():
                    return False
            except Exception as e:
                print(e)
                return False

        try:
            self.__client.send_data(feed, value)
            return True
        except RequestError as e:
            print(e)
            return False


class Paho:
    def __init__(self, host="mqtt", port=1883, AIO: AIO = AIO(), user=None, key=None):
        self.username = getenv("MQTT_USER") or user
        self.key = getenv("MQTT_KEY") or key
        self.AIO = AIO
        self.host = host
        self.port = port

    def on_message(self, client, userdata, message):
        print("message received  ", str(message.payload.decode("utf-8")))
        topic = message.topic.split("/")
        if topic[1] == "dispense-treat-toggle":
            self.AIO.send(topic[1], message.payload.decode("utf-8"))

    def on_connect(self, client, userdata, flags, rc):
        print("Connected flags ", str(flags), "result code ", str(rc))
        self.client.subscribe("stream/#")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print(client, userdata, mid, granted_qos)

    def run(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.key)
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        # self.client.tls_set()
        self.client.connect(self.host, self.port)
        self.client.loop_forever()


# Only run if it's enabled, implemented so it's off in dev environments
if getenv("ENABLE_AIO_BRIDGE"):
    print("AIO Bridge starting...")
    aio = AIO()
    my_mqtt = Paho()

    my_mqtt.run()
else:
    print("AIO Bridge exiting due to environment variable...")
