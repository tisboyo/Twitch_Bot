# Import standard python modules

# from main import AddOhmsBot
from twitchbot import cfg

# Import Adafruit IO REST client.
from Adafruit_IO import Client
from Adafruit_IO.errors import RequestError as RequestError

# to get stored credientials
from os import environ as secrets


class AIO:
    """AdafruitIO Class"""

    def __init__(self):
        # Secret can be set in either an environment variable (used first) or config.json
        self.ADAFRUIT_IO_USERNAME = secrets.get("ADAFRUIT_IO_USERNAME", False) or cfg.adafruit_io_user
        self.ADAFRUIT_IO_KEY = secrets.get("ADAFRUIT_IO_KEY", False) or cfg.adafruit_io_key

        # The connection handle for making calls
        self.__adafruit_io = None

        # Default to not connected
        self.AIO_CONNECTION_STATE = False
        self.ATTN_ENABLE = True

    def connect_to_aio(self):
        """Connect to Adafruit.IO"""
        # Create an instance of the REST client.
        try:
            print("Atempting to connect to AIO as " + self.ADAFRUIT_IO_USERNAME)
            self.__adafruit_io = Client(self.ADAFRUIT_IO_USERNAME, self.ADAFRUIT_IO_KEY)
            print("Connected to Adafruit.IO")
            self.AIO_CONNECTION_STATE = True
        except Exception:
            print("Failed to connect to AIO, disabling it")
            self.AIO_CONNECTION_STATE = False

    def send(self, feed):
        """Send to an AdafruitIO topic"""
        if self.AIO_CONNECTION_STATE is False:
            print("Not even trying, we aren't connected")
            return False
        try:
            self.__adafruit_io.send_data(feed, 1)
            return True
        except RequestError as e:
            print(e)
            return False


# def push_attn(feed="twitch-attn-indi"):
#     if AddOhmsBot.AIO_CONNECTION_STATE is False:
#         print("Not even trying, we aren't connected")
#         return False
#     try:
#         AddOhmsBot.Adafruit_IO.send_data(feed, 1)
#         return True
#     except RequestError as e:
#         print(e)
#         return False


# def increment_feed(feed="treat-counter-text"):
#     if AddOhmsBot.AIO_CONNECTION_STATE is False:
#         print("Not publishing, we aren't connected")
#         return False

#     feed_data = AddOhmsBot.Adafruit_IO.data(feed)  # returns an array of values
#     feed_value = int(feed_data[0].value)  # this feed only has 1

#     feed_value += 1

#     print("sending count: ", feed_value)
#     try:
#         AddOhmsBot.Adafruit_IO.send_data("treat-counter-text", feed_value)
#         return True
#     except RequestError as e:
#         print(e)
#         return False
