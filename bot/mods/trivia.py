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

from models import TriviaQuestions


class TriviaMod(Mod):
    name = "triviamod"

    def __init__(self):
        super().__init__()
        self.reset_question()
        self.msg_prefix: str = "❔"
        # Create session for participant tracking
        self.session = dict()
        self.score_board = dict()

    def reset_question(self):
        self.current_question: int = -1
        self.current_answer: int = -1
        self.current_participants: dict = dict()  # {username:(correct, incorrect)}
        self.almost_active = False
        self.active = False
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

    # This command will almost always be sent by the webserver,
    # setting the CommandContext to Whisper will allow it in whispers
    # only, but when sent over the command console, context is ignored.
    @SubCommand(trivia, "q", permission="bot")  # , context=CommandContext.WHISPER) #TODO
    async def trivia_q(self, msg: Message, question_num: int, answer_num: int):
        question_num, answer_num = int(question_num), int(answer_num)  # Framework only passes strings, convert it.

        print(f"Trivia question #{question_num}, Answer: {ascii_lowercase[answer_num-1].upper()}")

        # Don't send a question while another is active, queuing the next one.
        while self.active or self.almost_active:
            await sleep(0.5)

        self.almost_active = True  # Resets in reset_question

        # Don't set the question as active until it's sent to chat.
        self.current_question = question_num
        self.current_answer = answer_num

        result = session.query(TriviaQuestions).filter_by(id=self.current_question).one_or_none()

        self.answer_text = ascii_lowercase[answer_num - 1]
        if result is not None:
            await sleep(5)  # Sleep early to let the watchers catch up to the stream

            # Mark question as active
            self.active = True  # Resets in reset_question

            # Send the question to chat
            await msg.reply(f"{self.msg_prefix}{result.text}")
            await sleep(10)

            await msg.reply(f"{self.msg_prefix}15 seconds remaining")
            await sleep(10)
            await msg.reply(f"{self.msg_prefix}Final answers...")
            await sleep(5)

            correctly_answered = list()
            for participant in self.session:
                if (
                    self.session[participant]["q"].get(self.current_question, False)
                    and participant in self.current_question_participant  # See note in reset_session
                ):
                    correctly_answered.append(participant)

            if len(correctly_answered) > 0:
                correctly_answered = ", ".join(correctly_answered)
                await msg.reply(f"{self.msg_prefix} Congrats to {correctly_answered} for the correct answer.")

            self.reset_question()

    @SubCommand(trivia, "winner", permission="admin")
    async def trivia_winner(self, msg: Message):
        try:
            winners = self.score_board["winners"]
            most_correct = self.score_board["most_correct"]
            await msg.reply(f"{bot.msg_prefix} Congrats to {winners} for the most correct answers with {most_correct}")
            self.score_board = dict()  # Wipe the scoreboard

        except KeyError:
            await run_command("trivia", msg, ["end"], blocking=True)
            await run_command("trivia", msg, ["winner"], blocking=True)

    @SubCommand(trivia, "end", permission="bot")
    async def trivia_end(self, msg: Message):

        most_correct = 0
        leaderboard = str()
        for participant in self.session:
            if self.session[participant]["correct"] > most_correct:
                leaderboard = participant
                most_correct = self.session[participant]["correct"]

            elif self.session[participant]["correct"] == most_correct:
                # Tie between multiple participants
                leaderboard += f", {participant}"

        self.score_board["winners"] = leaderboard
        self.score_board["most_correct"] = most_correct

        # Clear the session data
        self.session = dict()

        await msg.reply(f"{bot.msg_prefix} Thanks for playing BaldEngineer Trivia!")

    async def on_raw_message(self, msg: Message):
        if (
            self.current_question > 0 and msg.is_privmsg and self.active
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
