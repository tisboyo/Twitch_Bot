from twitchbot import event_handler, Event, Message

print("on-channel-points-redemption.py loaded")


@event_handler(Event.on_channel_points_redemption)
async def on_channel_points_redemption(msg: Message, reward: str):
    print(f"Message: {msg}")
    print(f"Reward: {reward}")
