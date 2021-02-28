import asyncio
import json

from main import bot
from twitchbot.channel import Channel
from twitchbot.modloader import Mod
from twitchbot.poll.polldata import PollData


class PollsToMQTT(Mod):
    name = "PollsToMQTT"

    def __init__(self):
        super().__init__()
        self.mqtt = bot.MQTT

        # Set how quick to send poll updates
        self.update_frequency = 0.5

    def get_poll_setup(self, poll: PollData, active: bool = True) -> str:
        # Build the dictionary for poll setup
        poll_setup = dict(
            title=poll.title,
            total_duration=poll.duration_seconds,
            choices=poll.choices,
            active=active,
            update_frequency=self.update_frequency,
        )
        return json.dumps(poll_setup)

    def get_poll_data(self, poll: PollData) -> str:
        # Build the dictionary for poll data
        poll_data = dict(
            seconds_left=poll.seconds_left,
            votes=poll.votes,
            done=poll.done,
        )
        return json.dumps(poll_data)

    async def on_poll_started(self, channel: Channel, poll: PollData):

        # Send the setup data to MQTT
        setup_json = self.get_poll_setup(poll)
        await self.mqtt.send(self.mqtt.Topics.poll_setup, setup_json)

        # While the poll is running, send continuous updates
        while not poll.done:
            data_json = self.get_poll_data(poll)
            await self.mqtt.send(self.mqtt.Topics.poll_data, data_json)
            await asyncio.sleep(self.update_frequency)

    async def on_poll_ended(self, channel: Channel, poll: PollData):

        # Send final results
        data_json = self.get_poll_data(poll)
        await self.mqtt.send(self.mqtt.Topics.poll_data, data_json)

        # Sleep for 15 seconds before hiding the canvas
        await asyncio.sleep(15)

        # Send the setup data to MQTT
        setup_json = self.get_poll_setup(poll, active=False)
        await self.mqtt.send(self.mqtt.Topics.poll_setup, setup_json)
