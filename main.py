# Twitch bot written for the BaldEngineer channel
import os
import logging
import datetime

from twitchio.ext import commands

# Set logging level and format
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(name)s: %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self):
        irc_token = os.environ.get("twitch_oauth")
        nick = os.environ.get("twitch_nickname")
        prefix = os.environ.get("twitch_prefix")
        channel = os.environ.get("twitch_channel")

        super().__init__(
            irc_token=irc_token,
            api_token="test",
            nick=nick,
            prefix=prefix,
            initial_channels=[channel],
        )

        self.active_users = dict()
        self.max_users = 0
        self.topic = None
        self.start_time = None

    # Events don't need decorators when subclassed
    async def event_ready(self):
        logger.warning(f"Ready | {self.nick}")

    async def event_message(self, message):
        logger.debug(f"{message.author.display_name}: {message.content}")

        try:  # Count how many messages a user has sent.
            self.active_users[message.author.display_name] += 1
        except KeyError:
            self.active_users[message.author.display_name] = 1
        except Exception as e:
            logger.warning(e)

        # Check if more members are in the channel, and keep track of maximum
        if len(message.channel.chatters) > self.max_users:
            self.max_users = len(message.channel.chatters)

        # Handle any commands issued
        await self.handle_commands(message)

    @commands.command(name="active")
    async def active_users(self, ctx):
        await ctx.send(
            f"I have seen {len(self.active_users)} user{'s' if len(self.active_users) > 1 else ''} since starting."
        )

    @commands.command(name="max")
    async def send_max_users(self, ctx):
        await ctx.send(
            f"There have been a maximum of {self.max_users} users with us today."
        )

    @commands.command(name="start")
    async def start_stream(self, ctx):
        # Check to make sure only authorized user can use this command
        if not ctx.author.is_mod:
            return

        self.max_users = 0
        self.active_users = dict()
        self.start_time = datetime.datetime.now()

        # Set the topic while stripping out the command
        self.topic = " ".join(
            [s for s in ctx.content.split() if not s.startswith(ctx.prefix)]
        )

        await ctx.send(
            f"Starting stream{':' if len(self.topic) > 0 else ''} {self.topic}"
        )

    @commands.command(name="end")
    async def end_of_stream(self, ctx):
        # Check to make sure only authorized user can use this command
        if not ctx.author.is_mod:
            return

        await ctx.send(
            f"Thank you to the {len(self.active_users)} user{'s' if len(self.active_users) > 1 else ''} "
            f"that participated in our stream today. We had a total of {self.max_users} chatters with us."
        )
        await ctx.send(
            "To keep the conversation going, please join us on Discord at http://addohms.com/discord"
        )

        # Clean up our variables after a stream is over.
        self.start_time = None
        self.active_users = dict()
        self.max_users = 0
        self.topic = None

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        # self.start_time is None when a stream is not running.
        if self.start_time:
            uptime_delta = datetime.datetime.now() - self.start_time
            # Format uptime to HH:MM format. Change split to 3 to include seconds.
            uptime = ":".join(str(uptime_delta).split(":")[:2])

            await ctx.send(f"Stream uptime {uptime}")
        else:
            await ctx.send(f"Sorry, a stream hasn't been started yet.")

    @commands.command(name="topic")
    async def send_topic(self, ctx):

        # Check to make sure a topic is set
        if self.topic:
            ctx.send(f"Today's topic: {self.topic}")
        else:
            ctx.send("A topic is currently not defined.")


bot = Bot()
bot.run()
