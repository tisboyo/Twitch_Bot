from json import loads

from mods._database import session
from twitchbot import cfg
from twitchbot import get_pubsub
from twitchbot import Mod
from twitchbot import PubSubTopics

from models import Settings


class PubSub(Mod):
    """
    This class is used only to subscribe to pubsub topics.
    Handling of the responses should be handled in other Mods
    """

    name = "pubsub_subscribe"

    def __init__(self):
        super().__init__()

    async def loaded(self):
        query = session.query(Settings.value).filter(Settings.key == "twitch_pubsub_token").one_or_none()

        if query:
            access_token = loads(query[0])["access_token"]

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
                    access_token=access_token,
                )
                print(f"PubSub active for {channel}")
