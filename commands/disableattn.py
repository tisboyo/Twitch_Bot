from twitchbot import Command
from main import AddOhmsBot


@Command("disable_attn", permission="admin")
async def disable_attn(msg, *args):
    AddOhmsBot.ATTN_ENABLE = False
    await msg.reply("🤖going to be quiet now!")
