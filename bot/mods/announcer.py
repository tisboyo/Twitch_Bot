from asyncio import sleep
from datetime import datetime
from datetime import timedelta
from os import getenv
from zoneinfo import ZoneInfo

from main import bot
from mods._database import session
from mods.topic import get_topic
from twitchbot import add_task
from twitchbot import cfg
from twitchbot import channels
from twitchbot import Message
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import stop_task
from twitchbot import SubCommand
from twitchbot import task_exist

from models import AnnouncementCategories
from models import Announcements
from models import Settings

"""
!announce                             - Base command, doesn't do anything directly
!announce nosleep                     - Disables automatic sleep
!announce start                       - Re-enables announcements after being disabled (Sticky)
!announce stop                        - Disables announcements completely (Sticky)
!announce time {seconds:int}          - Sets the frequency of Announcements in seconds (Sticky)
!announce list                        - Lists all of the commands to the console
!announce del {ID:int}                - Deletes an announcement by ID. If message is the last in the active category,
                                      - resets active category to Default
!announce add {Message:str}           - Adds a new announcement to Default category
!announce enable {ID:int}             - Enables an announcement by ID
!announce disable {ID:int}            - Disables an announcement by ID
!announce status                      - Displays status in chat
!announce category                    - Base command, doesn't do anything directly
!announce category add {Name:str}     - Add a new category
!announce category del {ID:int}       - Deletes a category by ID
                                      -- Must not have any announcements assigned
                                      -- Can not delete Default
!announce category list               - Lists the available categories to the console
!announce category assign \           - Assign an announcement to a category
  {AnnouncementID:int} {CategoryID:int}
!announce category activate \         - Sets a category as active
  {CategoryID:int}
"""  # noqa W605


class AutoMessageStarterMod(Mod):
    name = "automsg"
    task_name = "automessage"

    def __init__(self):
        query = session.query(Settings.value).filter(Settings.key == "announcement_delay").one_or_none()
        self.delay = int(query[0]) if query is not None else 900
        self.chan = cfg.channels[0]
        self.next_run = datetime.min
        self.timezone = ZoneInfo("America/Chicago")
        self.channel_active = False
        self.announcements_sleeping = True
        self.sleep_override = False
        self.current_category_setting = "announcement_category"
        self.announcement_count = 0

        query = session.query(Settings.value).filter_by(key="announce_topic_frequency").one_or_none()
        self.announce_topic_frequency = int(query.value) if query is not None else 0

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
                    # Grab the currently enabled announcement category
                    cat = session.query(Settings).filter(Settings.key == self.current_category_setting).first()
                    category = self.get_announcements_category(cat.value) if not None else 1

                    if self.announcement_count >= self.announce_topic_frequency:
                        # Send the topic instead of the announcement
                        topic = get_topic()
                        message_text = "Topic: " + topic
                        self.announcement_count = 0
                    else:
                        result = (  # Read the next announcement from the database
                            session.query(Announcements)
                            .filter(Announcements.enabled == True)  # noqa E712 SQLAlchemy doesn't work with `is True`
                            .filter(Announcements.category == category.id)
                            .order_by(Announcements.last_sent)
                            .first()
                        )

                        # Make sure there are entries in the dictioary
                        if result is None:
                            # Use continue instead of return so more can be added once the bot is run
                            continue

                        message_text = result.text
                        self.announcement_count += 1

                        # Update the last time sent of the message
                        session.query(Announcements).filter(Announcements.id == result.id).update(
                            {"last_sent": datetime.now(), "times_sent": result.times_sent + 1}
                        )

                        session.commit()

                    # Send the message
                    await channels[self.chan].send_message(bot.msg_prefix + message_text)

                    # Since we sent a message, going to clear the announcements_sleeping flag
                    self.announcements_sleeping = False

                    # Assuming the channel isn't active until proven otherwise
                    self.channel_active = False

                elif not self.channel_active:
                    if not self.announcements_sleeping:
                        await channels[self.chan].send_message(bot.msg_prefix + "It's so quiet in here...")
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
        await msg.reply(f"{bot.msg_prefix}Announce auto-sleep status is now {status}.")

    @SubCommand(announce, "start", permission="admin")
    async def announce_start(self, msg, *args):
        self.enable = True
        print("Enabling announcements.")
        await channels[self.chan].send_message(f"{bot.msg_prefix}Announcements, announcements, ANNOUNCEMENTS!")
        session.query(Settings).filter(Settings.key == "announcement_enabled").update({"value": True})

        session.commit()

    @SubCommand(announce, "stop", permission="admin")
    async def announce_stop(self, msg, *args):
        self.enable = False
        print("Disabling announcements.")
        await channels[self.chan].send_message(f"{bot.msg_prefix}Disabling announcements")

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
            await msg.reply(f"{bot.msg_prefix}New announce time is {time} seconds")
        except ValueError:
            await msg.reply(f"{bot.msg_prefix}Invalid time, please use an integer in seconds")
        except TypeError:
            await msg.reply(f"{bot.msg_prefix} Current announce time is {self.delay} seconds.")
        except Exception as e:
            print(type(e), e)

    @SubCommand(announce, "list", permission="admin")
    async def announce_list(self, msg, *args):
        result = (
            session.query(Announcements, AnnouncementCategories)
            .order_by(Announcements.id)
            .join(AnnouncementCategories)
            .all()
        )
        print("Announcements".center(80, "*"))
        print("          Times")
        print(" ID : EN : Sent : Category : Text")
        for announcement, category in result:
            en = "Y" if announcement.enabled else "N"
            print(f"{announcement.id:3} :  {en} : {announcement.times_sent:4} : {category.name[:8]:8} : {announcement.text}")
        print(f" https://{getenv('WEB_HOSTNAME')}/announcements ".center(80, "*"))
        await msg.reply(f"{bot.msg_prefix}Announcements listed in console.")

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

        announcement = self.get_announcement(id)

        if announcement is None:
            print("Invalid Announcement delete ID, 0 rows deleted.")
        else:
            session.delete(announcement)
            print(f"Announcement id {announcement.id} deleted.")
            await msg.reply(f"{bot.msg_prefix}Announcement {id=} deleted.")

        count = session.query(Announcements).filter(Announcements.category == announcement.id).count()
        if count == 0 and announcement.id != 1:
            await msg.reply(f"{bot.msg_prefix}Resetting category to Default")
            session.query(Settings).filter(Settings.key == self.current_category_setting).update({Settings.value: 1})

        session.commit()

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

        await msg.reply(f"{bot.msg_prefix}Added announce {id=}")

    @SubCommand(announce, "disable", permission="admin")
    async def announce_disable(self, msg, *args):
        "Disables posting an announcement by ID"
        try:
            index = int(args[0])

        except IndexError:
            await msg.reply(f"{bot.msg_prefix} Try again with an ID")
            return

        except ValueError:
            if args[0] == "last":
                result = session.query(Announcements.id).order_by(Announcements.last_sent.desc()).first()
                index = result.id
                print(f"Disabling ID {index}")
            else:
                await msg.reply(f"{bot.msg_prefix} Try again with an ID Number")
                return

        except Exception as e:
            print(type(e), e)
            return

        successful = session.query(Announcements).filter(Announcements.id == index).update({"enabled": False})
        if successful:
            result = session.query(Announcements).filter(Announcements.id == index).one_or_none()
            print(f"Disabled announcement ID {index}")
            await msg.reply(f"{bot.msg_prefix}Disabled announcement ID {index}: {str(result.text)}")

            session.commit()

        else:
            print(f"Announcement ID {index} not found.")
            await msg.reply(f"{bot.msg_prefix}Announcement ID {index} not found.")

    @SubCommand(announce, "enable", permission="admin")
    async def announce_enable(self, msg, *args):
        "Disables posting an announcement by ID"
        try:
            index = int(args[0])

        except IndexError:
            await msg.reply(f"{bot.msg_prefix} Try again with an ID")
            return

        except ValueError:
            await msg.reply(f"{bot.msg_prefix} Try again with an ID Number")
            return

        except Exception as e:
            print(type(e), e)
            return

        successful = session.query(Announcements).filter(Announcements.id == index).update({"enabled": True})
        if successful:
            print(f"Enabled announcement ID {index}")
            await msg.reply(f"{bot.msg_prefix}Enabled announcement ID {index}")
            session.commit()

        else:
            print(f"Announcement ID {index} not found.")
            await msg.reply(f"{bot.msg_prefix}Announcement ID {index} not found.")

    @SubCommand(announce, "status", permission="admin")
    async def announce_status(self, msg, *args):
        """Sends the current status of the announcements"""

        status = "Enabled" if self.enable else "Disabled"
        next_run_seconds = self.next_run - datetime.now(self.timezone)
        enabled = session.query(Announcements).filter(Announcements.enabled == True).count()  # noqa E712
        total_count = session.query(Announcements).count()
        # Scalar returns the first element of the first result or None
        cat_id = int(session.query(Settings.value).filter(Settings.key == self.current_category_setting).scalar())
        category_name = session.query(AnnouncementCategories.name).filter(AnnouncementCategories.id == cat_id).scalar()
        announcements_in_cat = session.query(Announcements).filter(Announcements.category == cat_id).count()

        replies = [
            f"{bot.msg_prefix}Current status is {status}",
            f"{bot.msg_prefix}Current delay is {self.delay} seconds. ",
            f"{bot.msg_prefix}Next send time will be {self.next_run.strftime('%H:%M:%S')} which is in {str(next_run_seconds)[:-7]}.",  # noqa E501
            f"{bot.msg_prefix}{enabled}/{total_count} of all announcements enabled.",
            f"{bot.msg_prefix}Current category is {category_name}, with {announcements_in_cat} announcements",
        ]

        for reply in replies:
            await msg.reply(reply)

    @SubCommand(announce, "category", permission="admin")
    async def announce_category(self, msg, *args):
        """Base command for category management"""
        pass

    @SubCommand(announce, "topic_frequency", permission="admin")
    async def announce_topic(self, msg, frequency: int = 0):
        frequency = int(frequency)
        settings_key = "announce_topic_frequency"

        if old_frequency := session.query(Settings).filter_by(key=settings_key).one_or_none():
            old_frequency.value = frequency

        else:
            insert = Settings(key=settings_key, value=frequency)
            session.add(insert)

        session.commit()

        self.announce_topic_frequency = frequency
        await msg.reply(f"{bot.msg_prefix}Topic will be sent every {frequency} announcements.")

    @SubCommand(announce_category, "add", permission="admin")
    async def announce_category_add(self, msg, *args):
        """Add a category"""

        cat_name = " ".join(map(str, args))
        exists = session.query(AnnouncementCategories).filter(AnnouncementCategories.name == cat_name).count()
        if exists:
            await msg.reply(f"{bot.msg_prefix}Duplicate category name")
            return

        # Insert the new category into the database
        new_announcement = AnnouncementCategories(name=cat_name)
        session.add(new_announcement)
        session.commit()

        # Refresh to pull the ID inserted as
        session.refresh(new_announcement)
        await msg.reply(f"{bot.msg_prefix}{new_announcement.name} added as id {new_announcement.id}")

    @SubCommand(announce_category, "del", permission="admin")
    async def announce_category_del(self, msg, category_id: int):
        """Check if any messages are still assigned to this category, and refuse to delete if so"""

        category_id = int(category_id)

        # Quick fail if trying to delete default
        if category_id == 1:
            await msg.reply(f"{bot.msg_prefix}Default category will not be deleted.")
            return

        # Grab the category
        category = self.get_announcements_category(category_id)
        if category is None:
            await msg.reply(f"{bot.msg_prefix} Category id {category_id} does not exist.")
            return

        # Check to see if there are announcements still assigned to this category
        announcement_count = session.query(Announcements).filter(Announcements.category == category_id).count()
        if announcement_count > 0:
            await msg.reply(f"{bot.msg_prefix}{category.name} is not an empty category, aborting. 🚨🚨")
            return

        session.delete(category)
        session.commit()
        await msg.reply(f"{bot.msg_prefix}{category.name} ({category.id}) has been deleted.")

    @SubCommand(announce_category, "list", permission="admin")
    async def announce_category_list(self, msg, *args):
        """List the available categories"""
        result = session.query(AnnouncementCategories).order_by(AnnouncementCategories.id).all()

        print("Announcement Categories".center(80, "*"))
        print(" ID : Category")
        for category in result:
            print(f"{category.id:3} : {category.name}")

        print(f" https://{getenv('WEB_HOSTNAME')}/announcements ".center(80, "*"))
        await msg.reply(f"{bot.msg_prefix}Categories listed in console.")

    @SubCommand(announce_category, "assign", permission="admin")
    async def announce_category_assign(self, msg, announcement_id: int, category_id: int):
        """
        Assign a category to an Announcement
        Usage: !announce category assign message_id category_id
        """

        # Cast the ID's to ints
        announcement_id = int(announcement_id)
        category_id = int(category_id)

        # Check to make sure the announcement category exists
        # Keep inside parens, otherwise this assigns True to category on a good category
        # instead of the category itself
        if (category := self.get_announcements_category(category_id)) is None:
            await msg.reply(f"{bot.msg_prefix}Invalid category id")
            return

        # Check to make sure the announcement itself exists
        if not session.query(Announcements).filter(Announcements.id == announcement_id).count():
            await msg.reply(f"{bot.msg_prefix}Invalid announcement id")
            return

        # Update the announcement
        result = (
            session.query(Announcements)
            .filter(Announcements.id == announcement_id)
            .update({Announcements.category: category_id})
        )

        session.commit()

        # Send response of results
        if result:
            await msg.reply(f"{bot.msg_prefix}Announcement id {announcement_id} updated to category {category.name}")
        else:
            await msg.reply(f"{bot.msg_prefix}Unable to update.")

    @SubCommand(announce_category, "activate", permission="admin")
    async def announce_category_activate(self, msg, category_id: int):
        """
        Activate a category to be shown.
        Usage: !activate category category_id
        """

        category_id = int(category_id)

        # Verify the category is a valid one
        if (category := self.get_announcements_category(category_id)) is None:
            await msg.reply(f"{bot.msg_prefix}Invalid category id.")
            return

        # TODO Change to just an update, and do a alembic revision to insert a default after #79 is complete.
        updated = (
            session.query(Settings)
            .filter(Settings.key == self.current_category_setting)
            .update({Settings.value: category_id})
        )

        if not updated:  # Insert the key
            insert = Settings(key=self.current_category_setting, value=category_id)
            session.add(insert)

        session.commit()

        await msg.reply(f"{bot.msg_prefix}Active announcement category is now {category.name}")

    def get_announcements_category(self, category_id: int) -> AnnouncementCategories or None:
        """
        Returns an AnnouncementCategories object or None
        Use: if (category := self.get_announcements_category(category_id)) is None:
        """
        category_id = int(category_id)
        category = session.query(AnnouncementCategories).filter(AnnouncementCategories.id == category_id).first()
        # Have to check if a valid category was returned
        # to prevent a NoneType error if an invalid one is found
        if category is None:
            category = AnnouncementCategories(id=1, name="Default")

        return category

    def get_announcement(self, announcement_id: int) -> Announcements or None:
        announcement_id = int(announcement_id)
        announcement = session.query(Announcements).filter(Announcements.id == announcement_id).first()
        return announcement

    def restart_task(self):
        if task_exist(self.task_name):
            stop_task(self.task_name)

        add_task(self.task_name, self.timer_loop())

    async def on_connected(self):
        self.restart_task()
