from twitchbot import Command

from main import AddOhmsBot


@Command("discord")
async def discord(msg, *args):
    await msg.reply(f"{AddOhmsBot.msg_prefix}Keep the conversation going in discord at https://baldengineer.com/discord")
