import asyncio
import datetime
import json
import pathlib
import signal
from os import getenv

from aiofile import AIOFile
from gmqtt import Client as MQTTClient


STOP = asyncio.Event()


def on_connect(client, flags, rc, properties):
    print("Connected")
    client.subscribe("stream/#", qos=0)
    client.subscribe("trivia/#", qos=0)
    client.subscribe("bot/#", qos=0)


async def on_message(client, topic, payload, qos, properties):
    message_text = str(payload.decode("utf-8"))
    topic_split = topic.split("/")
    file = topic_split[0]
    file_path = pathlib.Path(__file__).resolve().parent / "logs" / f"{datetime.date.today().isoformat()}-{file}.json"

    # send to file
    async with AIOFile(file_path, "a+") as afp:
        data = json.dumps({"timestamp": datetime.datetime.now().isoformat(), "topic": topic, "message": message_text})
        await afp.write(data + "\n")
        await afp.fsync()


def on_disconnect(client, packet, exc=None):
    print("MQTT Disconnected")


def on_subscribe(client, mid, qos, properties):
    pass
    # print("SUBSCRIBED")


def ask_exit(*args):
    STOP.set()


async def main(broker_host: str, user: str, passwd: str):
    host = getenv("WEB_HOSTNAME") or "mqtt_logger"
    client = MQTTClient(client_id=host + "-twitchbot-" + str(datetime.datetime.now().timestamp()))

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    client.set_auth_credentials(user, passwd)

    await client.connect(broker_host, port=1883)

    await STOP.wait()
    await client.disconnect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    host = "mqtt"
    MQTT_USERNAME = getenv("MQTT_USER")
    MQTT_PASS = getenv("MQTT_KEY")

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main(host, MQTT_USERNAME, MQTT_PASS))
