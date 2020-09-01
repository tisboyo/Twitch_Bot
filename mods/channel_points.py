from twitchbot import cfg, Mod, Message, Event, PubSubData, get_pubsub, PubSubTopics
import asyncio

from aiofile import AIOFile

import baldaio
from main import AddOhmsBot

# from os import getenv


class ChannelPoints(Mod):
    def __init__(self):
        super().__init__()
        print("ChannelPoints loaded")

        # Create a key as the name of a reward, and a value of the function to call
        self.redemptions = {
            "highlighted-message": self.highlighted_message,
            "Give BaldEngineer a treat.": self.dispense_treat,
            "Get His Attention!": self.attention_attention,
        }

    async def loaded(self):
        for channel in cfg.channels:
            await get_pubsub().listen_to_channel(
                channel,
                [
                    PubSubTopics.channel_points,
                    PubSubTopics.moderation_actions,
                    PubSubTopics.bits,
                    PubSubTopics.channel_subscriptions,
                    PubSubTopics.bits_badge_notification,
                ],
                access_token=cfg.pubsub_oauth,
            )

    async def on_channel_points_redemption(self, msg: Message, reward: str):
        await self.points_redeemed(reward)

    async def on_pubsub_received(self, raw: PubSubData):

        # Dump to a log file
        if True:
            async with AIOFile("pubsub.log", "a") as afp:
                data = str(raw.raw_data)
                await afp.write(data + "\n")
                await afp.fsync()

        if len(raw.message_data) == 0:
            # Happens at startup, and possibly other times.
            return

        elif raw.is_channel_points_redeemed:
            r = raw.message_data["redemption"]["reward"]["title"]
            await self.points_redeemed(r)
        else:
            # Unknown pubsub received, print out the data
            print(raw.message_data)

    async def points_redeemed(self, reward: str):
        print("Redemption".center(80, "*"))
        try:
            # Call the function for the reward that was redeemed.
            await self.redemptions[reward]()

        except KeyError:
            # Don't have a function for the reward that was redeemed.
            print(f"Unknown reward redeemed - '{reward}'")

    async def dispense_treat(self):
        baldaio.increment_feed(feed="treat-counter-text")
        print("Dispensing a treat!")

    async def attention_attention(self):
        print("Hey!!!")
        print(AddOhmsBot.ATTN_ENABLE)
        if AddOhmsBot.ATTN_ENABLE == True:
            baldaio.push_attn(feed="twitch-attn-indi")
        else:
            print("Shhhhh....")

    async def highlighted_message(self):
        print("Highlighted message.")

