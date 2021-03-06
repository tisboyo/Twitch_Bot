# Added for #152
from asyncio import sleep
from string import ascii_lowercase

from main import bot
from mods._database import session
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.message import Message
from twitchbot.util import run_command
from twitchbot.util.twitch_api_util import get_user_id

from models import TriviaQuestions
from models import TriviaResults


class TriviaMod(Mod):
    name = "triviamod"

    def __init__(self):
        super().__init__()
        self.reset_question()
        self.msg_prefix: str = "❔"
        # Create session for participant tracking
        self.session = dict()
        self.leaderboard = dict()
        self.manual_delay: int = 0

        # Flag for sending instructions message when first question is sent.
        # Also used for interupting mid-question when trivia ends
        # Needs to survive question reset
        self.trivia_active = False

    def reset_question(self):
        self.current_question: int = -1
        self.current_answer: int = -1
        self.current_participants: dict = dict()  # {username:(correct, incorrect)}
        self.question_active = False
        self.almost_active = False
        self.answer_text = None

        # This was needed when doing dev work and manually resetting the date on questions without
        # restarting the bot or ending the session. In general it is un-needed because when the
        # session ends it wipes out self.session, but I don't see any harm in leaving it.
        # When this wasn't checked, it would congratulate the user who answered the same question
        # the last time it came around. This may be needed if we ever allow questions to repeat in
        # calendar day.
        self.current_question_participant = set()

    @ModCommand(name, "trivia", permission="admin")
    async def trivia(self, msg, *args):
        print("trivia")

    @SubCommand(trivia, "delay", permission="admin")
    async def delay(self, msg: Message, new_delay: int):
        """Adds a delay at the start of the next question"""
        self.manual_delay = int(new_delay)  # framework doesn't typecast

    # This command will almost always be sent by the webserver,
    # setting the CommandContext to Whisper will allow it in whispers
    # only, but when sent over the command console, context is ignored.
    @SubCommand(trivia, "q", permission="bot")  # , context=CommandContext.WHISPER) #TODO
    async def trivia_q(self, msg: Message, question_num: int, answer_num: int):
        question_num, answer_num = int(question_num), int(answer_num)  # Framework only passes strings, convert it.
        channel_id = await get_user_id(msg.channel.name)

        print(f"Trivia question #{question_num}, Answer: {ascii_lowercase[answer_num-1].upper()}")

        # Don't send a question while another is active, queuing the next one.
        while self.question_active or self.almost_active:
            await sleep(0.5)

        self.almost_active = True  # Resets in reset_question

        # Don't set the question as active until it's sent to chat.
        self.current_question = question_num
        self.current_answer = answer_num

        result = session.query(TriviaQuestions).filter_by(id=self.current_question).one_or_none()

        self.answer_text = ascii_lowercase[answer_num - 1]
        if result is not None:
            # Send a welcome message and instructions if this is the first question of the session
            if not self.trivia_active:
                await msg.reply(f"{bot.msg_prefix}Trivia incoming...")
                await msg.reply(
                    f"{self.msg_prefix}To play trivia, answer with a single letter message of your answer(case insensitive)."
                )
                self.trivia_active = True

            async def sleep_if_active(time: int) -> bool:
                """Sleeps if trivia is active, returns True if trivia is still active at the end of the sleep"""
                # If trivia is not active, we will speed past sending the messages to chat and finalize answers
                for _ in range(time * 2):
                    if self.trivia_active:
                        await sleep(0.5)
                    else:
                        return False

                return True

            # Mark question as active
            self.question_active = True  # Resets in reset_question

            # Sleep early to let the watchers catch up to the stream
            if await sleep_if_active(7 + self.manual_delay):
                # Send the question to chat
                await msg.reply(f"{self.msg_prefix}{result.text}")

            if await sleep_if_active(40):
                await msg.reply(f"{self.msg_prefix}15 seconds remaining")

            if await sleep_if_active(10):
                await msg.reply(f"{self.msg_prefix}Final answers...")

            # One last sleep to let people get final answers in.
            await sleep_if_active(5)

            correctly_answered = list()
            for participant in self.session:
                if (
                    self.session[participant]["q"].get(self.current_question, False)
                    and participant in self.current_question_participant  # See note in reset_session
                ):
                    correctly_answered.append(participant)
                    user_id = await get_user_id(participant)

                    query = (
                        session.query(TriviaResults)
                        .filter(TriviaResults.user_id == user_id, TriviaResults.channel == channel_id)
                        .one_or_none()
                    )  # Grab the current row
                    if query:  # Update it
                        query.trivia_points += 1  # type: ignore
                        query.questions_answered_correctly[self.current_question] = True

                    else:
                        # Insert if the row didn't exist.
                        query = TriviaResults(
                            user_id=user_id,
                            channel=channel_id,
                            questions_answered_correctly={self.current_question: True},
                            trivia_points=1,
                        )
                    # Update the query
                    session.add(query)
                    session.commit()

            if len(correctly_answered) > 0:
                correctly_answered = ", ".join(correctly_answered)
                # Check the total length, if over 500 characters shorten it.
                message = f"{self.msg_prefix} Congrats to {correctly_answered} for the correct answer."
                if len(message) > 500:
                    count = len(correctly_answered.split(", "))
                    message = f"{self.msg_prefix} Wow! {count} of you got it right! Congrats"

                await msg.reply(message)

            self.reset_question()

    @SubCommand(trivia, "winner", permission="admin")
    async def trivia_winner(self, msg: Message):
        if len(self.leaderboard) == 0:
            # Trivia hasn't ended yet, force end it.
            await run_command("trivia", msg, ["end"], blocking=True)

        first = self.leaderboard.popitem() if len(self.leaderboard) > 0 else None
        second = self.leaderboard.popitem() if len(self.leaderboard) > 0 else None
        third = self.leaderboard.popitem() if len(self.leaderboard) > 0 else None

        if third is not None:
            await msg.reply(f"{self.msg_prefix}In third place is {', '.join(third[1])} with {third[0]}")
            await sleep(5)

        if second is not None:
            await msg.reply(f"{self.msg_prefix}In second place is {', '.join(second[1])} with {second[0]}")
            await sleep(5)

        if first is not None:
            await msg.reply(f"{self.msg_prefix}In first place is {', '.join(first[1])} with {first[0]}")
            await msg.reply(f"{bot.msg_prefix}Congratulations to all of the trivia winners.")

        # Reset the leaderboard
        self.leaderboard = dict()

    @SubCommand(trivia, "end", permission="bot")
    async def trivia_end(self, msg: Message):

        # Will trigger interupting the current question.
        self.trivia_active = False

        # Give the bot just enough time to send the last message for the current question.
        await sleep(1)

        leaderboard = dict()

        # Assign the participant to how many they got correct on the leaderboard
        for participant in self.session:
            correct = self.session[participant]["correct"]
            if not leaderboard.get(correct, False):
                leaderboard[correct] = list()
            leaderboard[correct].append(participant)

        # Sort the leaderboard by score, lowest to highest so popitem can pull the bottom item
        leaderboard_order = sorted(leaderboard.keys(), key=lambda x: x)

        # Update the winners in the database
        if len(leaderboard_order) > 0:  # We have participants, update them
            # Grab channel ID for database insertion
            channel_id = await get_user_id(msg.channel.name)

            # Loop through the highest score as a winner
            for participant in leaderboard[leaderboard_order[0]]:
                user_id = await get_user_id(participant)
                # User should have already been in the database from answering the question
                if (
                    session.query(TriviaResults)
                    .filter(TriviaResults.user_id == user_id, TriviaResults.channel == channel_id)
                    .update({TriviaResults.total_wins: TriviaResults.total_wins + 1})
                ):
                    session.commit()

        # Sort the leaderboard and save it
        self.leaderboard = dict()
        for order_id in leaderboard_order:
            self.leaderboard[order_id] = leaderboard[order_id]

        # Clear the session data
        self.session = dict()

        await msg.reply(
            f"{bot.msg_prefix}Thank you for playing trivia! Stick around, @baldengineer will share the winners soon!"
        )

    async def on_raw_message(self, msg: Message):
        if (
            self.current_question > 0 and msg.is_privmsg and self.question_active
        ):  # Check if trivia is active and not a server message

            normalized: tuple = msg.normalized_parts  # type: ignore
            if len(normalized) == 1 and len(normalized[0]) == 1 and normalized[0] in ascii_lowercase:
                answer = normalized[0]

                # Create user dictionary if this is their first answer.
                author = msg.author
                if not self.session.get(author, False):
                    self.session[author] = dict()
                    self.session[author]["correct"] = 0
                    self.session[author]["incorrect"] = 0
                    self.session[author]["q"] = dict()

                # Track the participants for this question
                self.current_question_participant.add(author)  # See note in reset_session

                # Check if user has already provided an answer, only first answer accepted
                if not self.session[author].get(self.current_question, False):
                    if answer == self.answer_text:  # Correct answer
                        self.session[author]["q"][self.current_question] = True
                        self.session[author]["correct"] += 1
                    else:  # Incorrect
                        self.session[author]["q"][self.current_question] = False
                        self.session[author]["incorrect"] += 1
