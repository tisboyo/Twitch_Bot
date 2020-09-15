from twitchbot import cfg, Mod, Message, Event, get_pubsub, PubSubData, PubSubBits, PubSubTopics, channels, Channel
import asyncio

from aiofile import AIOFile

import baldaio
from main import AddOhmsBot
from data import save_data, load_data


class MqttNotifications(Mod):
    def __init__(self):
        super().__init__()
        print("MQTT Notifications loaded")

    async def on_channel_raided(self, channel: Channel, raider: str, viewer_count: int) -> None:
        """Send MQTT push when the channel is raided."""
        pass

    async def on_channel_host_success(self, channel: Channel, hoster: str, viewer_count: int) -> None:
        """
        This function doesn't actually exist in the library, and is being researched being added.
        It may not be possible.
        """
        pass

    async def on_channel_subscription(self, subscriber: str, channel: Channel, msg: Message) -> None:
        """Send MQTT push when a new follower subscribes"""
        pass

    async def on_pubsub_bits(self, raw: PubSubData, data: PubSubBits) -> None:
        """Send MQTT push when a user redeems bits"""
        pass
