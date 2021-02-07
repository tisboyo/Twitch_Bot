from main import AddOhmsBot
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
            AddOhmsBot.live = True
        else:
            AddOhmsBot.live = False

    @SubCommand(stream, "status", permission="admin")
    async def stream_status(self, msg: Message, *args):
        await msg.reply(f"{AddOhmsBot.msg_prefix} Stream status: {AddOhmsBot.live}, In the {AddOhmsBot.location}")

    @SubCommand(stream, "lab", permission="admin")
    async def stream_lab(self, msg: Message, *args):
        AddOhmsBot.location = "Lab"
        await msg.reply(f"{AddOhmsBot.msg_prefix} Location is now In the Lab")

    @SubCommand(stream, "office", permission="admin")
    async def stream_office(self, msg: Message, *args):
        AddOhmsBot.location = "Office"
        await msg.reply(f"{AddOhmsBot.msg_prefix} Location is now In the Office")
