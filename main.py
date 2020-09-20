import version_check  # noqa: F401

from twitchbot.bots import BaseBot
import asyncio

from baldaio import AIO as Adafruit_IO


class AddOhmsBot(BaseBot):
    AIO = Adafruit_IO()

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
