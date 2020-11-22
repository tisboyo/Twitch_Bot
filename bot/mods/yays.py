from main import AddOhmsBot
from twitchbot.message import Message
from twitchbot.modloader import Mod


class Yay(Mod):
    name = "yay"

    def __init__(self):
        pass

    async def on_raw_message(self, msg: Message):
        # If the message is a system message, we're done here
        if not msg.author or not msg.content:
            return

        if msg.content.find("balden3Yay") >= 0:
            AddOhmsBot.AIO.send("yay-toggle", 1)
