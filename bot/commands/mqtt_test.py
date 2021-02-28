from main import bot
from mqtt import MqttTopics
from twitchbot import Command
from twitchbot.message import Message


@Command("mqtttest", permission="admin")
async def mqtt_test(msg: Message, *args):
    if bot.user_ignored(str(msg.author)):
        return

    # Build the message
    message = ""
    for arg in args:
        message += f"{arg} "

    if await bot.MQTT.send(MqttTopics.test, message):
        await msg.reply(f"{bot.msg_prefix} Connection successful.")
    else:
        await msg.reply(f"{bot.msg_prefix} Connection error.")
