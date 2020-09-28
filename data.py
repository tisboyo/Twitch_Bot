import datetime
import json

from aiofile import AIOFile
from twitchbot import cfg


async def load_data(json_file: str, channel: str = cfg.channels[0]) -> dict:
    """Load the data file"""

    # Add the file extension
    json_file = f"jsons/{channel}-{json_file}.json"

    try:
        async with AIOFile(json_file, "r") as afp:
            data = json.loads(await afp.read())
            return data

    except FileNotFoundError:
        # Create the file because it didn't exist and return an empty dictionary
        async with AIOFile(json_file, "w+") as afp:
            await afp.write(json.dumps({}))

        return dict()


async def save_data(json_file: str, data: dict, channel: str = cfg.channels[0]) -> None:
    """Write the messages back to the file"""
    # Add the file extension
    if json_file[-5:] != ".json":
        json_file = f"{json_file}.json"

    # Prepend the folder name
    json_file = f"jsons/{channel}-{json_file}"

    try:
        dump = json.dumps(data, indent=4, default=json_object_helper)
        async with AIOFile(json_file, "w+") as afp:
            await afp.write(dump)

    except FileNotFoundError as e:
        print(e)


def json_object_helper(object):
    if isinstance(object, (datetime.date, datetime.datetime)):
        return object.isoformat()
