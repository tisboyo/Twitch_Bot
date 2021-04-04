import json
from os import getenv

import websockets
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

uri = "ws://bot:13337"


async def send_command_to_bot(cmd, args: list):

    try:
        # The command console doesn't like when integers are sent, so convert everything to a string
        clean_args = [str(x) for x in args]

        async with websockets.connect(uri) as s:
            # We don't actually need this, but we have to read it before the bot will accept commands
            await s.recv()
            # There are two entries returned, and we need to return both
            await s.recv()

            # Define the messages to send
            msg = dict(
                type="run_command",
                command=cmd,
                channel=getenv("TWITCH_CHANNEL"),
                args=clean_args,
            )

            await s.send((json.dumps(msg) + "\n").encode("utf8"))

            # Check if the message was successful
            resp = json.loads(await s.recv())
            if resp.get("type", "fail") != "success":
                raise HTTPException(status_code=503)

            # 204 is a No Content status code
            return Response(status_code=HTTP_204_NO_CONTENT)

    except ConnectionRefusedError:
        print("Unable to connect to bot for stream status change")
        raise HTTPException(status_code=503)

    except Exception as e:
        print(f"Unknown exception trying to send message to bot. {e}")
        raise HTTPException(status_code=503)


async def send_message_to_bot(data, message):
    try:
        async with websockets.connect(uri) as s:
            # We don't actually need this, but we have to read it before the bot will accept commands
            await s.recv()
            # There are two entries returned, and we need to return both
            await s.recv()

            msg = dict(
                type="send_privmsg",
                channel=getenv("TWITCH_CHANNEL"),
                message=message,
            )
            await s.send((json.dumps(msg) + "\n").encode("utf8"))

            # Check if the message was successful
            resp = json.loads(await s.recv())
            if resp.get("type", "fail") != "success":
                raise HTTPException(status_code=503)

            # 204 is a No Content status code
            return Response(status_code=HTTP_204_NO_CONTENT)

    except ConnectionRefusedError:
        print("Unable to connect to bot for new follow.")
        raise HTTPException(status_code=503)

    except Exception as e:
        print(f"Unknown exception trying to send message to bot. {e}")
        raise HTTPException(status_code=503)
