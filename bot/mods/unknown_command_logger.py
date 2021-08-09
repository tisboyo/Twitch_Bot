from datetime import datetime

from aiofile import AIOFile
from main import bot
from twitchbot import cfg
from twitchbot import CommandContext
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot.message import Message

unknown_command_file = "irc_logs/unknown-commands.log"


class UnknownCommandLogger(Mod):
    name = "unknown_command_logger"

    def __init__(self):
        super().__init__()
        print("Unknown Command Logger loaded")

    @ModCommand(name, "test", context=CommandContext.BOTH, permission="admin")
    async def test(self, msg: Message, *args):
        # Check if user is on ignore list
        if bot.user_ignored(str(msg.author)):
            return

    async def on_privmsg_received(self, msg: Message):
        """Check if a command exists, and log it if it doesn't."""
        try:

            first = msg.parts[0]
            if first[0] == cfg.prefix:
                # The bot framework never fires on_privmsg_received if it detects
                # that a message is a valid command, so all we have to do
                # is handle the ones that are not valid commands
                async with AIOFile(unknown_command_file, "a") as afp:
                    await afp.write(f"{str(datetime.now())}:{msg.author}:{msg.content} \n")

        except IndexError:
            # Blank message for some reason, giving up.
            return
