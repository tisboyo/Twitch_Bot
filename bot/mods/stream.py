from main import bot
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.message import Message


class StreamMod(Mod):
    name = "streammod"

    def __init__(self):
        super().__init__()

    @ModCommand(name, "stream", permission="admin")
    async def stream(self, msg: Message, *args):
        pass

    @SubCommand(stream, "live", permission="admin")
    async def stream_live(self, msg: Message, *args):
        if args[0] == "true":
            bot.live = True
            await msg.reply(f"{bot.msg_prefix}Hey @baldengineer, put your razor down! You're live!")
        else:
            bot.live = False
            await msg.reply(
                f"{bot.msg_prefix}Thank you for joining the stream! Keep the conversation going: https://bald.ee/discord"
            )

    @SubCommand(stream, "status", permission="admin")
    async def stream_status(self, msg: Message, *args):
        await msg.reply(f"{bot.msg_prefix} Stream status: {bot.live}, In the {bot.location}")

    @SubCommand(stream, "lab", permission="admin")
    async def stream_lab(self, msg: Message, *args):
        bot.location = "Lab"
        await msg.reply(f"{bot.msg_prefix} Location is now In the Lab")

    @SubCommand(stream, "office", permission="admin")
    async def stream_office(self, msg: Message, *args):
        bot.location = "Office"
        await msg.reply(f"{bot.msg_prefix} Location is now In the Office")
