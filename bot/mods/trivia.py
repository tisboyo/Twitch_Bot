# Added for #152
from main import bot
from mods._database import session
from twitchbot import cfg
from twitchbot import Channel
from twitchbot import channels
from twitchbot import CommandContext
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand

from models import Settings


class TriviaMod(Mod):
    name = "triviamod"

    def __init__(self):
        pass

    @ModCommand(name, "trivia", permission="admin")
    async def trivia(self, msg, *args):
        pass

    @SubCommand(trivia, "q")
    async def trivia_q(self, msg, *args):
        print(args)
        pass
