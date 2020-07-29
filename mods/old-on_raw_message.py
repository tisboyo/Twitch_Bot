import asyncio
from aiofile import AIOFile

from twitchbot import event_handler, Event, Message

from os import getenv


print("on_raw_message.py loaded")

# Enable by creating a .env file in the root with LOGIRC=1
@event_handler(Event.on_raw_message)
async def on_raw_message(msg: Message):

    if getenv("LOGIRC") == "1":
        print("logging enabled")
        async with AIOFile("irc.log", "a") as afp:
            await afp.write(str(msg) + "\n")
            await afp.fsync()

