from asyncio import sleep
from datetime import datetime
from json import dumps

from main import bot
from mqtt import MqttTopics
from twitchbot import Message
from twitchbot import Mod
from twitchbot.channel import Channel


new_chatter_topic = MqttTopics.new_chatter


class NewChatter(Mod):
    # Created for #160
    name = "newchatter"

    def __init__(self) -> None:
        super().__init__()
        print("newchatter loaded")
        self.seen_users = set()

    async def on_channel_joined(self, channel: Channel):
        # This will reset the seen users once the stream goes offline
        while True:
            if not bot.live:
                self.seen_users = set()

            await sleep(60)

    async def on_raw_message(self, msg: Message) -> None:
        """Increment the user message counter"""

        # Make sure the user actually sent a message,and it's not a whisper.
        if not msg.is_user_message or msg.is_whisper:
            return

        if msg.author not in self.seen_users:
            if not bot.user_ignored(msg.author):
                await bot.MQTT.send(new_chatter_topic, dumps({"author": msg.author, "timestamp": str(datetime.now())}))
                print(f"New chatter {msg.author} sent to MQTT.")

                # Track that we've seen the user
                self.seen_users.add(msg.author)
