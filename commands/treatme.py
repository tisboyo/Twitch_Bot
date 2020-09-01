from twitchbot import Command
import baldaio


@Command("treatme")
async def push_treat(msg, *args):
    if baldaio.push_treat("dispense-treat-toggle"):
        await msg.reply("🤖Teleporting a treat")
    else:
        await msg.reply("🤖I couldn't do that at the moment. Sorry ☹️")

    # baldaio.push_attn('dispense-treat-toggle')
