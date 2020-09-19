from twitchbot import Command, CommandContext
from main import AddOhmsBot


@Command("disable_attn", permission="admin", context=CommandContext.BOTH)
async def disable_attn(msg, *args):
    AddOhmsBot.ATTN_ENABLE = False
    await msg.reply("🤖going to be quiet now!")
