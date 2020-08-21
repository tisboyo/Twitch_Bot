from twitchbot.bots import BaseBot
from twitchbot import Command

import baldaio

AIO_CONNECTION_STATE = False
ATTN_ENABLE = True

@Command('treatme')
async def push_treat(msg, *args):
	print(baldaio.push_treat('dispense-treat-toggle'))
	#baldaio.push_attn('dispense-treat-toggle')
	await msg.reply('Teleporting a treat')

@Command('disable_attn')
async def disable_attn(msg, *args):
	global ATTN_ENABLE
	ATTN_ENABLE = False
	await msg.reply('going to be quiet now!')


class AddOhmsBot(BaseBot):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
	AddOhmsBot().run()