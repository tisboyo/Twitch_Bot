from random import choice

from main import AddOhmsBot
from twitchbot.message import Message
from twitchbot.modloader import Mod


class Yay(Mod):
    name = "yay"

    def __init__(self):
        self.count = 0
        self.count_to_send = 5
        self.people_that_yay = set()
        self.people_count_to_send = 2

    async def on_raw_message(self, msg: Message):
        # If the message is a system message, we're done here
        if not msg.author or not msg.content:
            return

        how_many_yays = msg.content.count("balden3Yay")
        if how_many_yays > 0:
            self.count += how_many_yays if how_many_yays <= 3 else 3
            self.people_that_yay.add(msg.author)

            print(f"Yay count: {self.count}")
        else:
            # If it doesn't include a Yay, we don't care about it at all
            return

        # Did a choice to add a little bit or random for other conditions later on
        if choice([self.send_on_message_count(), self.send_on_x_people()]):
            await AddOhmsBot.MQTT.send(AddOhmsBot.MQTT.Topics.yay_toggle, 1)

    def send_on_message_count(self):
        if self.count >= self.count_to_send:
            self.count = 0
            return True
        else:
            return False

    def send_on_x_people(self):
        if len(self.people_that_yay) >= self.people_count_to_send:
            self.people_that_yay = set()
            return True
        else:
            return False
