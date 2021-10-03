import datetime
import re
from asyncio import create_task
from asyncio import sleep

import aiohttp
from main import bot
from mods._database import session as db
from twitchbot import cfg
from twitchbot import Channel
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.message import Message
from twitchbot.util.command_util import run_command

from models import BotRegex
from models import KnownBots
from models import Settings


class AutoBan(Mod):
    name = "autoban"

    def __init__(self):
        super().__init__()
        print("AutoBan loaded")
        self.checked_for_autoban = set()
        self.autoban_enable = False  # Set to true for bans to actually happen

        self.autoban_list_patterns = dict()
        query = db.query(BotRegex).filter(BotRegex.enabled == True).all()  # noqa E712
        for each in query:
            self.autoban_list_patterns[each.id] = each.pattern

        create_task(self.update_json_list())

    async def update_json_list(self):
        # Bot lists are stored in /bot/configs/config.json
        url = cfg.bot_lists
        run = cfg.bot_lists_run  # Run the url lists

        if not url or not run:
            print("Bot auto ban lists not configured.")
            return

        # Make sure the last checked key exists in the database, if not insert it
        if not db.query(Settings.value).filter(Settings.key == "next_bot_check").one_or_none():
            ins = Settings(key="next_bot_check", value=datetime.datetime.min.isoformat())
            db.add(ins)
            db.commit()

        while True:
            query = db.query(Settings.value).filter(Settings.key == "next_bot_check").one_or_none()
            if not query:
                print("Problem getting next bot check time")
                return

            next_run_time = datetime.datetime.fromisoformat(query[0])
            if next_run_time > datetime.datetime.now():  # Not time to run yet, lets sleep until it is
                seconds_until_run = next_run_time - datetime.datetime.now()
                print(f"Known bot update sleeping until {query[0]}")
                await sleep(seconds_until_run.total_seconds())

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
                            print(f"Bot list 2 update: Next offset {offset}, of Total {count} ")
                            await sleep(3)

                    print(f"Done updating bot list 2 - {count} known bots.")
            except Exception as e:
                print("Unhandled error updating known bots lists ", type(e), e)

            # Sleep the routine until 4am
            next_run_time = datetime.datetime.combine(
                (datetime.date.today() + datetime.timedelta(days=1)), datetime.time(hour=4)
            )
            db.query(Settings).filter(Settings.key == "next_bot_check").update({Settings.value: next_run_time.isoformat()})
            db.commit()
            run_time = str(datetime.datetime.now() - start_time).split(".", 2)[0]
            print(f"Finshed updating bot list, took {run_time}")

    async def check_to_ban_user(self, user: str, channel: Channel):
        """Ban the user if all requirements are met"""
        if user is None or user in self.checked_for_autoban:
            return False

        async def do_ban(user: str):

            discord_message = f"{user} banned for being a bot."

            if self.autoban_enable:
                await channel.send_command(
                    f"ban {user} Banned for suspected bot activity. Please use twitch unban request if you think this is a mistake."  # noqa E501
                )
            else:
                discord_message += " (Test run)"

            query = db.query(Settings).filter(Settings.key == "ban_webhook").one_or_none()
            if query:
                async with aiohttp.ClientSession() as session:
                    response = await session.post(
                        query.value, json={"content": discord_message, "username": "TwitchBot: Autoban"}
                    )
                    if response.status == 204:
                        ic(f"{discord_message}")

        ic(f"Checking for auto ban for {user}")
        query = db.query(KnownBots).filter(KnownBots.botname == user).one_or_none()
        if query and query.enableblock:  # Bot is in the table, enabled to be blocked
            query.banned = True
            db.commit()

            print(f"Bot banning {user} from {channel.name}")
            await do_ban(user)
            return True

        for pattern in self.autoban_list_patterns.values():
            if re.match(pattern, user):
                print(f"Banning {user} for matching pattern {pattern}")
                await do_ban(user)
                return True

        # Keep our own cache of checked users
        self.checked_for_autoban.add(user)
        return False

    @ModCommand(name, "banbot", permission="admin")
    async def ban_user(self, msg: Message, user: str):
        """Manually ban a user as a bot"""
        await self.check_to_ban_user(user, msg.channel)

    @SubCommand(ban_user, "add", permission="admin")
    async def banbot_add(self, msg: Message, pattern: str):
        # Check if the regex is valid, return error if not.
        try:
            re.compile(pattern)
        except re.error:
            await msg.reply(f"{bot.msg_prefix}Invalid regex pattern.")
            return

        # Will not support a space in the pattern, but that doesn't matter because usernames can't have spaces
        query = db.query(BotRegex).filter(BotRegex.pattern == pattern).one_or_none()
        if query is None:
            # Pattern didn't exist, so add it.
            insert = BotRegex(pattern=pattern)
            db.add(insert)
            db.commit()
            db.refresh(insert)
            await msg.reply(f"{bot.msg_prefix}Adding {pattern} to auto ban list")

        else:
            await msg.reply(f"{bot.msg_prefix}That pattern is already in the database.")

        await run_command("banbot", msg, ["reset"])

    @SubCommand(ban_user, "reset", permission="admin")
    async def banbot_reset(self, msg: Message):
        self.checked_for_autoban = set()
        print("Auto ban checks reset")

    async def on_raw_message(self, msg: Message):
        # Check on new messages if the user should be banned
        await self.check_to_ban_user(msg.author, msg.channel)

    async def on_user_join(self, user: str, channel: Channel):
        # Check when a user join event triggers if the user should be banned
        await self.check_to_ban_user(user, channel)
