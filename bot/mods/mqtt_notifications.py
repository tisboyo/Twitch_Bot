from json import dumps

from main import bot
from twitchbot import Channel
from twitchbot import Message
from twitchbot import Mod
from twitchbot import PubSubData


class MqttNotifications(Mod):
    name = "mqttnotifications"

    def __init__(self):
        super().__init__()
        print("MQTT Notifications loaded")

    async def on_channel_raided(self, channel: Channel, raider: str, viewer_count: int) -> None:
        """Send MQTT push when the channel is raided."""
        if await bot.MQTT.send(bot.MQTT.Topics.channel_raid, raider):
            print(f"Raid by {raider} announced to MQTT")
        else:
            print(f"Unable to announce raid by {raider} to MQTT")

        if await bot.MQTT.send(bot.MQTT.Topics.twitch_attention_indicator):
            print("Notification sent for raid to noise maker")
        else:
            print("Unable to send raid to noise maker")

    async def on_channel_host_success(self, channel: Channel, hoster: str, viewer_count: int) -> None:
        """
        This function doesn't actually exist in the library, and is being researched being added.
        It may not be possible.
        """
        pass

    async def on_channel_subscription(self, subscriber: str, channel: Channel, msg: Message) -> None:
        """Send MQTT push when a new follower subscribes"""
        # TODO How many months? Is this data accessible
        if await bot.MQTT.send(bot.MQTT.Topics.channel_sub):
            print(f"Publishing {subscriber} has Subscribed to the channel to MQTT")
        else:
            print(f"Unable to publish {subscriber} has subsbribed to the channel to MQTT")

    async def on_pubsub_bits(self, raw: PubSubData, data) -> None:
        """Send MQTT push when a user redeems bits"""
        # No usable data provided in raw or data :(
        if data.username is None:
            data.username = "AnAnonymousCheerer"

        send_data = dumps({"username": data.username, "bits": data.bits_used, "total_bits": data.total_bits_used})

        if await bot.MQTT.send(bot.MQTT.Topics.channel_cheer, send_data):
            print(f"Cheer announced to MQTT. {send_data}")
        else:
            print("Unable to announce Cheer to MQTT")
