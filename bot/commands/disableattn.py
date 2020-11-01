from main import AddOhmsBot
from twitchbot import Command
from twitchbot import CommandContext


@Command("disable_attn", permission="admin", context=CommandContext.BOTH)
async def disable_attn(msg, *args):
    AddOhmsBot.ATTN_ENABLE = False
    await msg.reply(f"{AddOhmsBot.msg_prefix}going to be quiet now!")
