import asyncio

from main import AddOhmsBot
from mods._database import session
from twitchbot import cfg
from twitchbot import channels
from twitchbot import Message
from twitchbot import Mod
from twitchbot import PubSubData
from twitchbot.channel import Channel
from twitchbot.command import ModCommand
from twitchbot.command import SubCommand
from twitchbot.config import get_nick
from twitchbot.poll.polldata import PollData

from models import Settings
from models import Wigs


class Wigs_mod(Mod):
    name = "wigs"

    def __init__(self):
        super().__init__()
        print("Wigs loaded")

    async def on_pubsub_received(self, raw: PubSubData):
        # Custom Channel Points redeemed
        if len(raw.message_data) == 0:
            # Happens at startup, and possibly other times.
            return

        elif raw.is_channel_points_redeemed:
            reward = raw.message_data["redemption"]["reward"]["title"]

            if reward == "Wear A Wig":
                channel = channels.get(cfg.channels[0])
                await self.wear_a_wig(channel)

    async def wear_a_wig(self, channel: Channel):
        print("starting wig poll")

        title = session.query(Settings.value).filter(Settings.key == "WigPollTitle").one_or_none()
        time = session.query(Settings.value).filter(Settings.key == "WigPollTime").one_or_none()
        choices = session.query(Wigs.wig_name).filter(Wigs.enabled == True).all()  # noqa #712

        # Cleanup the query data
        title, time = title[0], int(time[0])
        choices = [choice[0] for choice in choices]

        # The poll can't have a blank title and must have choices
        if title == "" or len(choices) == 0:
            await channel.send_message(f"{AddOhmsBot.msg_prefix} Wig poll isn't configured yet.")
            return

        # Create the poll object, and start the poll
        poll = PollData(channel, get_nick(), f"{AddOhmsBot.msg_prefix}{title}", time, *choices)
        await poll.start()

        while poll.seconds_left > 0:
            # print("Poll seconds left", poll.seconds_left)
            await asyncio.sleep(1)
        else:
            results = poll.votes.most_common()

            winner_count = 0
            # Check for a tie
            if len(results) > 1:  # More than one thing voted for
                if results[0][1] == results[1][1]:  # The top two have the same number of votes
                    # We have a tie, lets re-run the poll
                    new_choices = list()
                    key = results[0][1]
                    for r in results:  # Build the new list of choices
                        if r[1] == key:
                            new_choices.append(poll.choices[r[0] - 1])

                    # Run runoff poll
                    await asyncio.sleep(3)  # Let the previous results get posted
                    runoff_poll = PollData(channel, get_nick(), f"{AddOhmsBot.msg_prefix}RUNOFF:{title}", time, *new_choices)
                    await runoff_poll.start()
                    while runoff_poll.seconds_left > 0:
                        # Sleep while the poll runs
                        # print("Runoff poll seconds left", runoff_poll.seconds_left)
                        await asyncio.sleep(1)

                    results = runoff_poll.votes.most_common()
                    winner = runoff_poll.choices[results[0][0] - 1]

                    # Check to see if there is a tie AGAIN
                    key = results[0][1]

                    for r in results:  # Build the new list of choices
                        if r[1] == key:
                            winner_count += 1

                else:  # The top two were not the same, so the top wins
                    winner_count += 1
                    winner = poll.choices[results[0][0] - 1]
            else:  # Only one thing was voted for
                winner_count += 1
                winner = poll.choices[results[0][0] - 1]

            if winner_count > 1:
                await channel.send_message(f"{AddOhmsBot.msg_prefix}Chat can't decide, it's @baldengineer choice!")
            else:
                await channel.send_message(f"{AddOhmsBot.msg_prefix}Chat has spoken, @baldengineer should wear {winner}")

    @ModCommand(name, "wig", permission="admin", help="Available subcommands: poll, time, add, del, list, enable, disable")
    async def wig(self, msg, *args):
        pass

    @SubCommand(wig, "poll", permission="admin")
    async def wig_poll(self, msg: Message, *args):
        await self.wear_a_wig(msg.channel)

    @SubCommand(wig, "time", permission="admin", syntax="<seconds>", help="Set the duration of wig polls.")
    async def wig_time(self, msg: Message, time: int):
        """Set how long the poll should run for"""
        time = int(time)

        session.query(Settings.value).filter(Settings.key == "WigPollTime").update({Settings.value: time})
        session.commit()

        await msg.reply(f"{AddOhmsBot.msg_prefix}Time updated to {time}")

    @SubCommand(wig, "add", permission="admin", syntax="<text>", help="Add a new wig!")
    async def wig_add(self, msg: Message, *args):
        """Adds a new wig to the database"""
        wig_name = " ".join(map(str, args))

        new_wig = Wigs(wig_name=wig_name, enabled=1)
        session.add(new_wig)
        session.commit()

        session.refresh(new_wig)
        await msg.reply(f"{AddOhmsBot.msg_prefix}New wig added as id {new_wig.id}.")

    @SubCommand(wig, "del", permission="admin", syntax="<id>", help="Delete a wig by ID")
    async def wig_del(self, msg: Message, id: int):
        """Delete a wig by ID"""
        id = int(id)

        wig: Wigs = session.query(Wigs).filter(Wigs.id == id).first()
        if wig is not None:
            session.delete(wig)
            session.commit()
            await msg.reply(f"{AddOhmsBot.msg_prefix}{wig.wig_name} deleted.")

    @SubCommand(wig, "list", permission="admin", help="Lists the available wigs")
    async def wig_list(self, msg: Message, *args):
        wigs: Wigs = session.query(Wigs).all()
        wig_list = [f"{'🔕' if not wig.enabled else '🔔'}({wig.id}){wig.wig_name}" for wig in wigs]

        for w in wig_list:
            await msg.reply(f"{AddOhmsBot.msg_prefix} {w}")

    @SubCommand(wig, "disable", permission="admin", syntax="<id>", help="Disables a wig")
    async def wig_disable(self, msg: Message, id: int):
        id = int(id)

        wig: Wigs = session.query(Wigs).filter(Wigs.id == id).first()
        successful = session.query(Wigs).filter(Wigs.id == id).update({Wigs.enabled: False})

        if successful:
            await msg.reply(f"{AddOhmsBot.msg_prefix}{wig.wig_name} disabled.")

    @SubCommand(wig, "enable", permission="admin", syntax="<id>", help="Enables a wig")
    async def wig_enable(self, msg: Message, id: int):
        id = int(id)

        wig: Wigs = session.query(Wigs).filter(Wigs.id == id).first()
        successful = session.query(Wigs).filter(Wigs.id == id).update({Wigs.enabled: True})

        if successful:
            await msg.reply(f"{AddOhmsBot.msg_prefix}{wig.wig_name} enabled.")
