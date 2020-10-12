from main import AddOhmsBot
from twitchbot import Command


@Command("discord")
async def discord(msg, *args):
    await msg.reply(f"{AddOhmsBot.msg_prefix}Keep the conversation going in discord at https://baldengineer.com/discord")
