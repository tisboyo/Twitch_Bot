import asyncio
from aiofile import AIOFile
import json


async def load_data(json_file: str) -> dict:
    """Load the data file"""

    # Add the file extension
    json_file = f"jsons/{json_file}.json"

    try:
        async with AIOFile(json_file, "r") as afp:
            data = json.loads(await afp.read())
            return data

    except FileNotFoundError:
        # Create the file because it didn't exist and return an empty dictionary
        async with AIOFile(json_file, "w+") as afp:
            await afp.write(json.dumps({}))

        return dict()


async def save_data(json_file: str, data: dict) -> None:
    """Write the messages back to the file"""
    # Add the file extension
    json_file = f"jsons/{json_file}.json"

    try:
        async with AIOFile(json_file, "w+") as afp:
            await afp.write(json.dumps(data))

    except FileNotFoundError as e:
        print(e)
