from twitchbot import Command
import baldaio


@Command("treatme")
async def push_treat(msg, *args):
    print(baldaio.push_treat("dispense-treat-toggle"))
    # baldaio.push_attn('dispense-treat-toggle')
    await msg.reply("Teleporting a treat")
