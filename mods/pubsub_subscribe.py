from twitchbot import cfg, Mod, get_pubsub, PubSubTopics


class PubSub(Mod):
    """
    This class is used only to subscribe to pubsub topics.
    Handling of the responses should be handled in other Mods
    """

    def __init__(self):
        super().__init__()

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
            print(f"PubSub active for {channel}")
