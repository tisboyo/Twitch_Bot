import asyncio

import version_check  # noqa: F401
from alembic import config as alembic_config
from baldaio import AIO as Adafruit_IO
from twitchbot.bots import BaseBot


# Update database models
alembicArgs = ["--raiseerr", "upgrade", "head"]
alembic_config.main(argv=alembicArgs)


class AddOhmsBot(BaseBot):
    AIO = Adafruit_IO()
    msg_prefix = "🤖 "
    ATTN_ENABLE = True

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    bot = AddOhmsBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Shutting down the bot... ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.shutdown())
        print("Bye")
