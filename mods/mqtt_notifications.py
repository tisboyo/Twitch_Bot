from twitchbot import Mod, Message, PubSubData, Channel


from main import AddOhmsBot


class MqttNotifications(Mod):
    def __init__(self):
        super().__init__()
        print("MQTT Notifications loaded")

    async def on_channel_raided(self, channel: Channel, raider: str, viewer_count: int) -> None:
        """Send MQTT push when the channel is raided."""
        if AddOhmsBot.AIO.send("channel-raid", raider):
            print(f"Raid by {raider} announced to AIO")
        else:
            print(f"Unable to announce raid by {raider} to AIO")

    async def on_channel_host_success(self, channel: Channel, hoster: str, viewer_count: int) -> None:
        """
        This function doesn't actually exist in the library, and is being researched being added.
        It may not be possible.
        """
        pass

    async def on_channel_subscription(self, subscriber: str, channel: Channel, msg: Message) -> None:
        """Send MQTT push when a new follower subscribes"""
        # TODO How many months? Is this data accessible
        if AddOhmsBot.AIO.send("channel-subscription"):
            print(f"Publishing {subscriber} has Subscribed to the channel to AIO")
        else:
            print(f"Unable to publish {subscriber} has subsbribed to the channel to AIO")

    async def on_pubsub_bits(self, raw: PubSubData, data) -> None:
        """Send MQTT push when a user redeems bits"""
        # No usable data provided in raw or data :(
        if AddOhmsBot.AIO.send("channel-cheer"):
            print("Cheer announced to AIO")
        else:
            print("Unable to announce Cheer to AIO")
