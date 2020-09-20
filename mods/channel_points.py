from twitchbot import cfg, Mod, Message, PubSubData, channels

from main import AddOhmsBot


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

    async def on_channel_points_redemption(self, msg: Message, reward: str):
        await self.points_redeemed(reward)

    async def on_pubsub_received(self, raw: PubSubData):

        if len(raw.message_data) == 0:
            # Happens at startup, and possibly other times.
            return

        elif raw.is_channel_points_redeemed:
            r = raw.message_data["redemption"]["reward"]["title"]
            await self.points_redeemed(r)
        elif raw.is_bits:
            # Bits received, nothing to do here
            pass
        else:
            # Unknown pubsub received, print out the data
            print(f"Unknown pubsub received: {raw.message_data}")

    async def points_redeemed(self, reward: str):

        print("Redemption".center(80, "*"))
        try:
            # Call the function for the reward that was redeemed.
            await self.redemptions[reward]()

        except KeyError:
            # Don't have a function for the reward that was redeemed.
            print(f"Unknown reward redeemed - '{reward}'")

    async def dispense_treat(self, channel=cfg.channels[0]):
        if AddOhmsBot.AIO.send("dispense-treat-toggle"):
            await channels[channel].send_message("🤖Teleporting a treat")
        else:
            # chan = cfg.channels[0]
            await channels[channel].send_message("🤖I couldn't do that at the moment. Sorry ☹️")

        print("Dispensing a treat!")

    async def attention_attention(self, channel=cfg.channels[0]):
        print("Hey!!!")
        if AddOhmsBot.ATTN_ENABLE:
            if not AddOhmsBot.AIO.send("twitch-attn-indi"):
                # chan = cfg.channels[0]
                await channels[channel].send_message("🤖Something went wrong getting my attention. ☹️")

        else:
            print("Shhhhh....")

    async def highlighted_message(self):
        print("Highlighted message.")
