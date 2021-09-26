import datetime
from asyncio import create_task
from asyncio import sleep

import aiohttp
from mods._database import session as db
from twitchbot import cfg
from twitchbot import Channel
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot.message import Message

from models import KnownBots


class AutoBan(Mod):
    name = "autoban"

    def __init__(self):
        super().__init__()
        print("AutoBan loaded")

        create_task(self.update_json_list())

    async def update_json_list(self):
        # Bot lists are stored in /bot/configs/config.json
        url = cfg.bot_lists
        run = cfg.bot_lists_run  # Run the url lists

        if not url or not run:
            print("Bot auto ban lists not configured.")
            return

        while True:
            print("Updating known bot list")
            start_time = datetime.datetime.now()
            try:
                if run[0]:
                    print("Updating bot list 1...")
                    async with aiohttp.ClientSession() as session:
                        response = await session.get(url=url[0])

                        # Get the response as a json object.
                        response_js = await response.json()

                    bots = response_js["bots"]
                    count = response_js["_total"]
                    bot_list = list()

                    for b in bots:
                        name = b[0]
                        bot_list.append(name)

                    query = db.query(KnownBots.botname).filter(KnownBots.botname.in_(bot_list)).all()
                    for q in query:
                        bot_list.remove(q[0])

                    if bot_list:
                        ins_list = list()
                        for name in bot_list:
                            ins_list.append(KnownBots(botname=name, added_timestamp=datetime.datetime.now()))
                            print(f"{name} inserted into bot database.")

                        db.bulk_save_objects(ins_list)
                        db.commit()
                        del ins_list

                    print(f"Done updating bot list 1 - {count} known bots.")

                if run[1]:
                    print("Updating bot list 2...")
                    offset = 0
                    count = 1  # Temporary setting to let the while loop run

                    # This endpoint only returns 100 at a time
                    while offset < count:
                        async with aiohttp.ClientSession() as session:

                            response = await session.get(url=f"{url[1]}?offset={offset}")
                            ic(f"Retrieved url 2, offset {offset}")

                            # Get the response as a json object.
                            response_js = await response.json()

                        bots = response_js["bots"]
                        count = response_js["total"]
                        bot_list = list()

                        for b in bots:
                            name = b["username"]
                            bot_list.append(name)

                        query = db.query(KnownBots.botname).filter(KnownBots.botname.in_(bot_list)).all()
                        for q in query:
                            bot_list.remove(q[0])

                        if bot_list:
                            ins_list = list()
                            for name in bot_list:
                                ins_list.append(KnownBots(botname=name, added_timestamp=datetime.datetime.now()))
                                print(f"{name} inserted into bot database.")

                            db.bulk_save_objects(ins_list)
                            db.commit()
                            del ins_list

                        ic(f"Finished bot list 2 offset at {offset}")
                        offset += 100
                        if offset < count:
                            await sleep(3)

                    print(f"Done updating bot list 2 - {count} known bots.")
            except Exception as e:
                print("Unhandled error updating known bots lists ", type(e), e)

            # Sleep the routine until 4am
            next_run_time = datetime.datetime.combine(
                (datetime.date.today() + datetime.timedelta(days=1)), datetime.time(hour=4)
            )
            run_in = next_run_time - datetime.datetime.now()
            run_time = str(datetime.datetime.now() - start_time).split(".", 2)[0]
            print(f"Finshed updating bot list, took {run_time}")
            await sleep(run_in.total_seconds())

    @ModCommand(name, "ban", permission="admin")
    async def ban_user(self, msg: Message, *args):
        pass

    async def on_channel_joined(self, channel: Channel):
        # Need to sleep just to make sure the the command isn't missed.
        await sleep(1)

    async def on_raw_message(self, msg: Message):

        pass
