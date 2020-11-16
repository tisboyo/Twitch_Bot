# Import standard python modules
from datetime import datetime
from datetime import timedelta
from os import getenv
from typing import Union

from Adafruit_IO import Client
from Adafruit_IO.errors import RequestError as RequestError

from mods._database_models import session
from mods._database_models import Settings


class AIO:
    """AdafruitIO Class"""

    def __init__(self):
        # Secret can be set in either an environment variable (used first) or config.json
        self.ADAFRUIT_IO_USERNAME = getenv("ADAFRUIT_IO_USERNAME")
        self.ADAFRUIT_IO_KEY = getenv("ADAFRUIT_IO_KEY")

        # The connection handle for making calls
        self.__client = None
        self.last_sent_time = dict()
        self.mqtt_cooldown = dict()

        # Default to not connected
        self.AIO_CONNECTION_STATE = False
        self.ATTN_ENABLE = True

    def connect_to_aio(self):
        """Connect to Adafruit.IO"""
        # Create an instance of the REST client.
        if self.ADAFRUIT_IO_USERNAME is None or self.ADAFRUIT_IO_KEY is None:
            print("Adafruit IO keys not found, aborting connection")
            return False

        try:
            print("Atempting to connect to AIO as " + self.ADAFRUIT_IO_USERNAME)
            self.__client = Client(self.ADAFRUIT_IO_USERNAME, self.ADAFRUIT_IO_KEY)
            print("Connected to Adafruit.IO")
            self.AIO_CONNECTION_STATE = True
            return True

        except Exception as e:
            print("Failed to connect to AIO, disabling it")
            print(e)
            self.AIO_CONNECTION_STATE = False
            return False

    def get_cooldown(self, feed: str):
        """
        Returns the cooldown
        Loads it from the database,
        or returns 0 if one is not set.
        """
        if feed not in self.mqtt_cooldown:
            q = session.query(Settings.value).filter(Settings.key == f"mqtt_cooldown_{feed}").one_or_none()
            if q is None:
                # Value wasn't in the database, lets insert it.
                insert = Settings(key=f"mqtt_cooldown_{feed}", value=0)
                session.add(insert)
                self.mqtt_cooldown[feed] = 0
            else:
                self.mqtt_cooldown[feed] = int(q[0])

        return self.mqtt_cooldown[feed]

    def set_cooldown(self, feed: str, cooldown: int) -> None:
        """
        Sets the MQTT cooldown
        Updates or inserts the value into the database
        Exception handling should be done in the calling function
        """
        try:
            q = session.query(Settings.id).filter(Settings.key == f"mqtt_cooldown_{feed}").one_or_none()
            if q is None:
                # Value wasn't in the database, lets insert it.
                insert = Settings(key=f"mqtt_cooldown_{feed}", value=cooldown)
                session.add(insert)
                self.mqtt_cooldown[feed] = cooldown
            else:
                session.query(Settings).filter(Settings.key == f"mqtt_cooldown_{feed}").update({"value": cooldown})
                self.mqtt_cooldown[feed] = cooldown

            session.commit()
        except Exception as e:
            session.rollback()
            print("SQLAlchemy Error, rolling back.")
            print(e)

    def send(self, feed, value: Union[str, int] = 1):
        """Send to an AdafruitIO topic"""
        last_sent = self.last_sent_time.get(feed, datetime.min)
        cooldown = self.get_cooldown(feed)
        now = datetime.now()

        if (last_sent + timedelta(seconds=cooldown)) > now:
            print(f"MQTT {feed} on cooldown for {(last_sent + timedelta(seconds=cooldown)) - now}.")
            return False

        if self.AIO_CONNECTION_STATE is False:
            try:
                if not self.connect_to_aio():
                    return False
            except Exception as e:
                print(e)
                return False

        try:
            self.__client.send_data(feed, value)
            self.last_sent_time[feed] = now
            return True
        except RequestError as e:
            print(e)
            return False
