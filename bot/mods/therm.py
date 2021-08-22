from twitchbot import Mod
from twitchbot.message import Message


class ThermMod(Mod):
    name = "thermmod"

    def __init__(self):
        super().__init__()
        print("Thermmod loaded")

    async def on_raw_message(self, msg: Message):
        if msg.content is None:
            return

        content: str = msg.content
        if content.startswith("/ban @th3rmite"):
            await msg.reply("@Th3rmite has been banned.")
