from twitchbot import event_handler, Event, Message

print("on_channel_points_redemption.py loaded")


@event_handler(Event.on_channel_points_redemption)
async def on_channel_points_redemption(msg: Message, reward: str):
    print(f"Message: {msg}")
    print(f"Reward: {reward}")

    redemptions = {
        "33d50c71-f1ae-4e47-8106-3abc84954922": dispense_treat,
    }

    try:
        # Call the function for the reward that was redeemed.
        redemptions[reward]()

    except IndexError:
        # Don't have a function for the reward that was redeemed.
        pass


async def dispense_treat():
    print("Dispensing a treat!")
