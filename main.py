from twitchbot.bots import BaseBot
from twitchbot import Command

AIO_CONNECTION_STATE = False
ATTN_ENABLE = True

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