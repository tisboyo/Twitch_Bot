from main import bot
from mqtt import MqttTopics
from twitchbot import CommandContext
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot.message import Message


class FollowMod(Mod):
    name = "followmod"

    def __init__(self):
        super().__init__()
        print("FollowMod loaded")

    @ModCommand(name, "follow", context=CommandContext.CONSOLE)
    async def follow(self, msg: Message, follower, *args):

        await msg.reply(f"{bot.msg_prefix} Thanks for the follow {follower}")
        await bot.MQTT.send(MqttTopics.channel_follow, follower)
