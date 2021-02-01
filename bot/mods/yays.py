from helpers.points import Points
from main import AddOhmsBot
from twitchbot.message import Message
from twitchbot.modloader import Mod


class Yay(Mod):
    name = "yay"

    def __init__(self):
        self.points = Points(emojis=5, unique_users=2, emoji_cap=3)

    async def on_raw_message(self, msg: Message):
        # If the message is a system message, we're done here
        if not msg.author or not msg.content:
            return

        how_many_yays = msg.content.count("balden3Yay")
        if how_many_yays > 0:
            if self.points.check(msg, emojis=how_many_yays):
                await AddOhmsBot.MQTT.send(AddOhmsBot.MQTT.Topics.yay_toggle, 1)

            print(self.points.status())

        else:
            # If it doesn't include a Yay, we don't care about it at all
            return
