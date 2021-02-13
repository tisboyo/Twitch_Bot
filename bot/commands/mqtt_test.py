from main import AddOhmsBot
from mqtt import MqttTopics
from twitchbot import Command


@Command("mqtttest", permission="admin")
async def mqtt_test(msg, *args):
    # Build the message
    message = ""
    for arg in args:
        message += f"{arg} "

    if await AddOhmsBot.MQTT.send(MqttTopics.test, message):
        await msg.reply(f"{AddOhmsBot.msg_prefix} Connection successful.")
    else:
        await msg.reply(f"{AddOhmsBot.msg_prefix} Connection error.")
