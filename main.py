from twitchbot.bots import BaseBot

from baldaio import AIO


class AddOhmsBot(BaseBot):

    # Establish the Adafruit.IO handle to use by plugins
    aio = AIO()

    def __init__(self):
        super().__init__()
        # Connect to Adafruit.IO
        self.aio.connect_to_aio()


if __name__ == "__main__":
    AddOhmsBot().run()
