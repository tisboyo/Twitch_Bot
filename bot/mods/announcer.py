from asyncio import sleep
from datetime import datetime
from datetime import timedelta
from os import getenv

import pytz
from main import AddOhmsBot
from mods._database_models import Announcements
from mods._database_models import session
from mods._database_models import Settings
from twitchbot import add_task
from twitchbot import cfg
from twitchbot import channels
from twitchbot import Message
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import stop_task
from twitchbot import SubCommand
from twitchbot import task_exist


class AutoMessageStarterMod(Mod):
    name = "automsg"
    task_name = "automessage"

    def __init__(self):
        query = session.query(Settings.value).filter(Settings.key == "announcement_delay").one_or_none()
        self.delay = int(query[0]) if query is not None else 900
        self.chan = cfg.channels[0]
        self.next_run = datetime.min
        self.timezone = pytz.timezone("America/Chicago")
        self.channel_active = False
        self.announcements_sleeping = True
        self.sleep_override = False

        self.enable = session.query(Settings.value).filter(Settings.key == "announcement_enabled").one_or_none()
        if self.enable is None:
            insert = Settings(key="announcement_enabled", value=True)
            session.add(insert)

    @property
    def delay(self):
        return self.__delay

    @delay.setter
    def delay(self, time: int):
        self.__delay = int(time)
        print(f"Announcement message delay is {self.delay} seconds")

    async def timer_loop(self):
        while True:
            # Try except to prevent loop from accidentally crashing, no known reasons to crash.
            try:
                now = datetime.now(tz=self.timezone)
                self.next_run = now + timedelta(seconds=self.delay)
                await sleep(self.delay)
                # This is done so the loop will continue to run and not exit out because the loop has ended
                # if done as a while enabled
                if self.enable and (self.channel_active or self.sleep_override):
                    result = (  # Read the next announcement from the database
                        session.query(Announcements)
                        .filter(Announcements.enabled == True)  # noqa E712 SQLAlchemy doesn't work with `is True`
                        .order_by(Announcements.last_sent)
                        .first()
                    )

                    # Make sure there are entries in the dictioary
                    if result is None:
                        # Use continue instead of return so more can be added once the bot is run
                        continue

                    # Send the message
                    await channels[self.chan].send_message(AddOhmsBot.msg_prefix + result.text)

                    # Update the last time sent of the message
                    session.query(Announcements).filter(Announcements.id == result.id).update(
                        {"last_sent": datetime.now(), "times_sent": result.times_sent + 1}
                    )

                    session.commit()

                    # Since we sent a message, going to clear the announcements_sleeping flag
                    self.announcements_sleeping = False

                    # Assuming the channel isn't active until proven otherwise
                    self.channel_active = False

                elif not self.channel_active:
                    if not self.announcements_sleeping:
                        await channels[self.chan].send_message(AddOhmsBot.msg_prefix + "It's so quiet in here...")
                        self.announcements_sleeping = True

            except Exception as e:
                print(e)

    async def on_raw_message(self, msg: Message):
        """
        Tracks the last time a message was sent,
        and if it was by the bot, consider the channel inactive.
        """
        if msg.is_user_message:
            self.channel_active = True
            self.announcements_sleeping = False

    @ModCommand(name, "announce", permission="admin")
    async def announce(self, msg, *args):
        # Announce parent command
        pass

    @SubCommand(announce, "nosleep", permission="admin")
    async def announce_nosleep(self, msg, *args):
        self.sleep_override = not self.sleep_override
        status = "disabled" if self.sleep_override else "enabled"
        await msg.reply(f"{AddOhmsBot.msg_prefix}Announce auto-sleep status is now {status}.")

    @SubCommand(announce, "start", permission="admin")
    async def announce_start(self, msg, *args):
        self.enable = True
        print("Enabling announcements.")
        await channels[self.chan].send_message(f"{AddOhmsBot.msg_prefix}Announcements, announcements, ANNOUNCEMENTS!")
        session.query(Settings).filter(Settings.key == "announcement_enabled").update({"value": True})

        session.commit()

    @SubCommand(announce, "stop", permission="admin")
    async def announce_stop(self, msg, *args):
        self.enable = False
        print("Disabling announcements.")
        await channels[self.chan].send_message(f"{AddOhmsBot.msg_prefix}Disabling announcements")

        session.query(Settings).filter(Settings.key == "announcement_enabled").update({"value": False})

        session.commit()

    @SubCommand(announce, "time", permission="admin")
    async def announce_time(self, msg, time: int = None):
        try:
            # Make sure we receive a positive number
            if int(time) < 1:
                raise ValueError

            self.delay = int(time)

            updated = session.query(Settings).filter(Settings.key == "announcement_delay").update({"value": self.delay})

            if not updated:
                # Insert if it wasn't updated, because it didn't exist.
                insert = Settings(key="announcement_delay", value=self.delay)
                session.add(insert)

            session.commit()

            self.restart_task()
            await msg.reply(f"{AddOhmsBot.msg_prefix}New announce time is {time} seconds")
        except ValueError:
            await msg.reply(f"{AddOhmsBot.msg_prefix}Invalid time, please use an integer in seconds")
        except TypeError:
            await msg.reply(f"{AddOhmsBot.msg_prefix} Current announce time is {self.delay} seconds.")
        except Exception as e:
            print(type(e), e)

    @SubCommand(announce, "list", permission="admin")
    async def announce_list(self, msg, *args):
        result = session.query(Announcements).order_by(Announcements.id).all()

        print("Announcements".center(80, "*"))
        print("          Times")
        print(" ID : EN : Sent : Text")
        for each in result:
            en = "Y" if each.enabled else "N"
            print(f"{each.id:3} :  {en} : {each.times_sent:4} : {each.text}")
        print(f" https://{getenv('WEB_HOSTNAME')}/announcements ".center(80, "*"))
        await msg.reply(f"{AddOhmsBot.msg_prefix}Announcements listed in console.")

    @SubCommand(announce, "del", permission="admin")
    async def announce_del(self, msg, *args):

        try:
            id = args[0]
            id = int(id)
        except IndexError:
            print("Invalid Announcement delete value not provided")
            return
        except ValueError:
            print("Invalid Announcement delete ID passed, must be an integer")
            return
        except Exception as e:
            print(e)
            return

        result = session.query(Announcements).filter(Announcements.id == id).delete()
        if not result:
            print("Invalid Announcement delete ID, 0 rows deleted.")
        else:
            print(f"{result} Announcement deleted.")
            await msg.reply(f"{AddOhmsBot.msg_prefix}Announcement {id=} deleted.")

    @SubCommand(announce, "add", permission="admin")
    async def announce_add(self, msg, *args):

        message = ""

        # Build the message
        for arg in args:
            message += f"{arg} "

        print(f"Adding to announce: {message}", end="")

        announcement_object = Announcements(text=message)

        session.add(announcement_object)
        session.commit()
        session.refresh(announcement_object)
        id = announcement_object.id

        print(f"...done, {id=}")

        await msg.reply(f"{AddOhmsBot.msg_prefix}Added announce {id=}")

    @SubCommand(announce, "disable", permission="admin")
    async def announce_disable(self, msg, *args):
        "Disables posting an announcement by ID"
        try:
            index = int(args[0])

        except IndexError:
            await msg.reply(f"{AddOhmsBot.msg_prefix} Try again with an ID")
            return

        except ValueError:
            if args[0] == "last":
                result = session.query(Announcements.id).order_by(Announcements.last_sent.desc()).first()
                index = result.id
                print(f"Disabling ID {index}")
            else:
                await msg.reply(f"{AddOhmsBot.msg_prefix} Try again with an ID Number")
                return

        except Exception as e:
            print(type(e), e)
            return

        successful = session.query(Announcements).filter(Announcements.id == index).update({"enabled": False})
        if successful:
            result = session.query(Announcements).filter(Announcements.id == index).one_or_none()
            print(f"Disabled announcement ID {index}")
            await msg.reply(f"{AddOhmsBot.msg_prefix}Disabled announcement ID {index}: {str(result.text)}")

            session.commit()

        else:
            print(f"Announcement ID {index} not found.")
            await msg.reply(f"{AddOhmsBot.msg_prefix}Announcement ID {index} not found.")

    @SubCommand(announce, "enable", permission="admin")
    async def announce_enable(self, msg, *args):
        "Disables posting an announcement by ID"
        try:
            index = int(args[0])

        except IndexError:
            await msg.reply(f"{AddOhmsBot.msg_prefix} Try again with an ID")
            return

        except ValueError:
            await msg.reply(f"{AddOhmsBot.msg_prefix} Try again with an ID Number")
            return

        except Exception as e:
            print(type(e), e)
            return

        successful = session.query(Announcements).filter(Announcements.id == index).update({"enabled": True})
        if successful:
            print(f"Enabled announcement ID {index}")
            await msg.reply(f"{AddOhmsBot.msg_prefix}Enabled announcement ID {index}")
            session.commit()

        else:
            print(f"Announcement ID {index} not found.")
            await msg.reply(f"{AddOhmsBot.msg_prefix}Announcement ID {index} not found.")

    @SubCommand(announce, "status", permission="admin")
    async def announce_status(self, msg, *args):
        """Sends the current status of the announcements"""

        status = "Enabled" if self.enable else "Disabled"
        next_run_seconds = self.next_run - datetime.now(self.timezone)
        enabled = session.query(Announcements).filter(Announcements.enabled == True).count()  # noqa E712
        total_count = session.query(Announcements).count()
        replies = [
            f"{AddOhmsBot.msg_prefix}Current status is {status}",
            f"{AddOhmsBot.msg_prefix}Current delay is {self.delay} seconds. ",
            f"{AddOhmsBot.msg_prefix}Next send time will be {self.next_run.strftime('%H:%M:%S')} which is in {str(next_run_seconds)[:-7]}.",  # noqa E501
            f"{AddOhmsBot.msg_prefix}{enabled}/{total_count} of announcements enabled.",
        ]

        for reply in replies:
            await msg.reply(reply)

    def restart_task(self):
        if task_exist(self.task_name):
            stop_task(self.task_name)

        add_task(self.task_name, self.timer_loop())

    async def on_connected(self):
        self.restart_task()
