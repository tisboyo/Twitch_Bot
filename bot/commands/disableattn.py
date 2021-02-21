from main import bot
from twitchbot import Command
from twitchbot import CommandContext


@Command("disable_attn", permission="admin", context=CommandContext.BOTH)
async def disable_attn(msg, *args):
    bot.ATTN_ENABLE = False
    await msg.reply(f"{bot.msg_prefix}going to be quiet now!")
