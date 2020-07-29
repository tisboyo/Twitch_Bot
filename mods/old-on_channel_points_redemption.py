from twitchbot import event_handler, Event, Message
from playsound import playsound

import baldaio

print("on_channel_points_redemption.py loaded")


@event_handler(Event.on_channel_points_redemption)
async def on_channel_points_redemption(msg: Message, reward: str):
    print(f"Message: {msg}")
    print(f"Reward: {reward}")

    redemptions = {
       # "33d50c71-f1ae-4e47-8106-3abc84954922": dispense_treat,
       "53d1a5ca-db4a-4b36-8f13-b90443fbc402" : dispense_treat,
       "2b02b005-be3d-48fe-bb33-40851c87fc8c" : attention_attention
    }

    try:
        # Call the function for the reward that was redeemed.
        redemptions[reward]()

    except IndexError:
        # Don't have a function for the reward that was redeemed.
        print("Unhandled reward.")
        pass

def dispense_treat():
    baldaio.increment_feed(feed='treat-counter-text')
    print("Dispensing a treat!")

def attention_attention():
    print("Hey!!!")
    baldaio.push_attn(feed='twitch-attn-indi')
#   playsound('error.wav')