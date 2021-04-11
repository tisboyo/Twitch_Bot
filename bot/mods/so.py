from main import bot
from mods._database import session
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.channel import Channel
from twitchbot.message import Message

from models import Settings


class ShoutoutMod(Mod):
    name = "shoutoutmod"

    def __init__(self):
        super().__init__()
        self.last_raid = None

    @ModCommand(name, "so", permission="so")
    async def shoutout(self, msg: Message, *args):
        if len(args) == 0 and self.last_raid:
            # Shotout to last raided user
            shoutout_to = self.last_raid
        elif len(args) == 0:
            shoutout_to = None
        else:
            shoutout_to = args[0]

        # If we a user isn't defined to shoutout to, quit
        if shoutout_to is None:
            return

        # Read the message from the settings table
        message = session.query(Settings.value).filter(Settings.key == "shoutout_msg").one_or_none()

        # Default message if none has been set.
        if message is None:
            message = "Hey Everyone! Check out the awesome {channel}. Give them a follow!"
        else:
            message = message[0]

        message = message.format(channel=shoutout_to)

        await msg.reply(f"{bot.msg_prefix}{message}")

    @SubCommand(shoutout, "msg", permission="admin")
    async def shoutout_msg(self, msg: Message, *args):

        message = ""
        for word in args:
            message += f"{word} "

        successful = session.query(Settings.value).filter(Settings.key == "shoutout_msg").update({"value": message})
        if not successful:
            insert = Settings(key="shoutout_msg", value=message)
            session.add(insert)

        session.commit()

        await msg.reply(f"{bot.msg_prefix} Message updated.")

    async def on_channel_raided(self, channel: Channel, raider: str, viewer_count: int):
        # Update who just raided
        self.last_raid = raider
