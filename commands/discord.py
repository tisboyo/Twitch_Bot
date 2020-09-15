from twitchbot import Command


@Command("discord")
async def discord(msg, *args):
    await msg.reply("🤖Keep the conversation going in discord at https://baldengineer.com/discord")
