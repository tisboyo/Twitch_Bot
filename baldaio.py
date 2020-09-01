# Import standard python modules
import time
import aio_secrets

from main import AddOhmsBot

# Import Adafruit IO REST client.
from Adafruit_IO import Client, Feed
from Adafruit_IO.errors import RequestError as RequestError

# to get stored credientials
from os import environ as secrets

ADAFRUIT_IO_KEY = secrets["ADAFRUIT_IO_KEY"]
ADAFRUIT_IO_USERNAME = secrets["ADAFRUIT_IO_USERNAME"]

aio = None


def connect_to_aio():
    global aio
    # Create an instance of the REST client.
    try:
        print("Atempting to connect to AIO as " + ADAFRUIT_IO_USERNAME)
        aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
        print("Connected")
        AddOhmsBot.AIO_CONNECTION_STATE = True
    except:
        print("Failed to connect to AIO, disabling it")
        AddOhmsBot.AIO_CONNECTION_STATE = False


def push_treat(feed="dispense-treat-toggle"):
    global aio
    if AddOhmsBot.AIO_CONNECTION_STATE == False:
        print("Not even trying, we aren't connected")
        return False
    try:
        aio.send_data(feed, 1)
        return True
    except RequestError as e:
        print(e)
        return False


def push_attn(feed="twitch-attn-indi"):
    global aio
    if AddOhmsBot.AIO_CONNECTION_STATE == False:
        print("Not even trying, we aren't connected")
        return False
    try:
        aio.send_data(feed, 1)
        return True
    except RequestError as e:
        print(e)
        return False


def increment_feed(feed="treat-counter-text"):
    global aio
    if AddOhmsBot.AIO_CONNECTION_STATE == False:
        print("Not publishing, we aren't connected")
        return False

    feed_data = aio.data(feed)  # returns an array of values
    feed_value = int(feed_data[0].value)  # this feed only has 1

    feed_value += 1

    print("sending count: ", feed_value)
    try:
        aio.send_data("treat-counter-text", feed_value)
        return True
    except RequestError as e:
        print(e)
        return False


connect_to_aio()
# increment_feed()
