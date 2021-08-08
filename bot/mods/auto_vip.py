from asyncio import sleep

from main import bot
from twitchbot import cfg
from twitchbot import Channel
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot.enums import MessageType
from twitchbot.message import Message
from twitchbot.permission import perms

# Note requires affiliate account to test!


class AutoVIPMod(Mod):
    name = "autovipmod"

    def __init__(self):
        super().__init__()
        self.vip_group = "vip"
        print("AutoVIP loaded")

    @ModCommand(name, "vipupdate", permission="admin")
    async def vip_update(self, msg: Message, *args):
        # Need to sleep just to make sure the the command isn't missed.
        await sleep(1)
        await msg.channel.send_message("/vips")

    async def on_channel_joined(self, channel: Channel):
        # Need to sleep just to make sure the the command isn't missed.
        await sleep(1)
        await channel.send_message("/vips")

    async def on_raw_message(self, msg: Message):

        if msg.type is MessageType.NOTICE and msg.msg_id == "vips_success":
            # Split the message on the colon which removes the preamble
            temp_parse = msg.normalized_content.split(":", maxsplit=1)
            # We only care about the userlist, overwrite with just that
            temp_parse = temp_parse[1]
            # strip off the leading space and trailing period
            temp_parse = temp_parse[:-1].strip()
            # split them into a list
            vip_users = temp_parse.split(", ")

            channel = cfg.channels[0]
            vip_group: dict = perms.get_group(channel, self.vip_group)

            # For users that are twitch vips add them to the bot vip group
            for user in vip_users:
                if user not in vip_group["members"]:
                    perms.add_member(channel, self.vip_group, user)
                    print(f"{user} was added to bot vip group.")

            # Check if there are users in the bot's vip list and notify about/remove them
            for user in vip_group["members"]:
                if user not in vip_users:
                    perms.delete_member(channel, self.vip_group, user)
                    print(f"{user} was removed from the bot vip group.")

            await msg.reply(f"{bot.msg_prefix} Shout out to the VIPs! You all rock. Thank You.")
