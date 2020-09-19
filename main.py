from twitchbot.bots import BaseBot

from baldaio import AIO as Adafruit_IO


class AddOhmsBot(BaseBot):
    AIO = Adafruit_IO()

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    AddOhmsBot().run()
