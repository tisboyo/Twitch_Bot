from main import AddOhmsBot
from twitchbot import Command


@Command("treatme")
async def push_treat(msg, *args):
    if AddOhmsBot.aio.send("dispense-treat-toggle"):
        await msg.reply("🤖Teleporting a treat")
    else:
        await msg.reply("🤖I couldn't do that at the moment. Sorry ☹️")

    # baldaio.push_attn('dispense-treat-toggle')
