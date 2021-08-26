# Import standard python modules
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from os import getenv
from typing import Union

from gmqtt import Client
from mods._database import session

from models import Settings


@dataclass
class MqttTopics:
    stream_prefix = "stream/"
    treat_in_queue = stream_prefix + "treat-in-queue"
    dispense_treat_toggle = stream_prefix + "dispense-treat-toggle"
    twitch_attention_indicator = stream_prefix + "twitch-attn-indi"
    treat_status = stream_prefix + "treat_status"
    channel_raid = stream_prefix + "channel-raid"
    channel_sub = stream_prefix + "channel-subscription"
    channel_cheer = stream_prefix + "channel-cheer"
    channel_follow = stream_prefix + "channel-follow"
    yay_toggle = stream_prefix + "yay-toggle"
    poll_setup = stream_prefix + "poll/setup"
    poll_data = stream_prefix + "poll/data"
    verify_1k = stream_prefix + "verify1k"
    test = stream_prefix + "mqtttest"
    first_time_chatter = stream_prefix + "first_time_chatter"
    new_chatter = stream_prefix + "new_chatter"

    trivia_prefix = "trivia/"
    trivia_setup = trivia_prefix + "setup"
    trivia_data = trivia_prefix + "data"
    trivia_leaderboard = trivia_prefix + "trivia/leaderboard"


class MQTT:
    """MQTT Class"""

    def __init__(self):
        # Secret can be set in either an environment variable (used first) or config.json
        self.MQTT_USERNAME = getenv("MQTT_USER")
        self.MQTT_PASS = getenv("MQTT_KEY")

        # The connection handle for making calls
        self.__client = None
        self.last_sent_time = dict()
        self.mqtt_cooldown = dict()
        self.hostname = "mqtt"
        self.client_id = getenv("WEB_HOSTNAME") + "-twitchbot-" + str(datetime.now().timestamp())

        # Default to not connected
        self.MQTT_CONNECTION_STATE = False
        self.ATTN_ENABLE = True

        self.Topics = MqttTopics

    async def connect_to_mqtt(self):
        """Connect to MQTT Server"""
        # Create an instance of the REST client.
        if self.MQTT_USERNAME is None or self.MQTT_PASS is None:
            print("MQTT keys not found, aborting connection")
            return False

        try:
            print("Atempting to connect to MQTT as " + self.MQTT_USERNAME)
            self.__client = Client(client_id=self.client_id)
            self.__client.set_auth_credentials(self.MQTT_USERNAME, self.MQTT_PASS)
            await self.__client.connect(self.hostname, port=1883)
            print("Connected to MQTT")
            self.MQTT_CONNECTION_STATE = True
            return True

        except Exception as e:
            print("Failed to connect to MQTT, disabling it")
            print(e)
            self.MQTT_CONNECTION_STATE = False
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

    async def send(self, feed, value: Union[str, int] = 1, retain: bool = False):
        """Send to an MQTT topic"""
        last_sent = self.last_sent_time.get(feed, datetime.min)
        cooldown = self.get_cooldown(feed)
        now = datetime.now()

        if (last_sent + timedelta(seconds=cooldown)) > now:
            print(f"MQTT {feed} on cooldown for {(last_sent + timedelta(seconds=cooldown)) - now}.")
            return False

        if self.MQTT_CONNECTION_STATE is False:
            try:
                if not await self.connect_to_mqtt():
                    return False
            except Exception as e:
                print(e)
                return False

        try:
            self.__client.publish(feed, value, retain=retain)
            self.last_sent_time[feed] = now
            return True
        except Exception as e:
            print(e)
            return False
