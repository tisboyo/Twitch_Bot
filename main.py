from twitchbot.bots import BaseBot
from twitchbot import Command

import baldaio


class AddOhmsBot(BaseBot):

    AIO_CONNECTION_STATE = False
    ATTN_ENABLE = True

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    AddOhmsBot().run()
