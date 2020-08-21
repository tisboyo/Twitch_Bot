import asyncio
from aiofile import AIOFile

from twitchbot import Event, Message, Mod, cfg


class TwitchLog(Mod):
    def __init__(self):
        super().__init__()
        print("TwitchLog loaded")

    async def on_raw_message(self, msg: Message):

        if True:
            async with AIOFile("irc.log", "a") as afp:
                await afp.write(str(msg) + "\n")
                await afp.fsync()

