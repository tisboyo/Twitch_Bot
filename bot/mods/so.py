from main import bot
from mods._database import session
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.message import Message

from models import Settings


class ShoutoutMod(Mod):
    name = "shoutoutmod"

    def __init__(self):
        super().__init__()
        self.last_raid = None

    @ModCommand(name, "so", permission="admin")
    async def shoutout(self, msg: Message, *args):
        if len(args) == 0:
            # Shotout to last raided user
            shoutout_to = self.last_raid
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

        print(message)
