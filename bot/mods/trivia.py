# Added for #152
from asyncio import sleep
from string import ascii_lowercase

from main import bot
from mods._database import session
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.message import Message

from models import TriviaQuestions


class TriviaMod(Mod):
    name = "triviamod"

    def __init__(self):
        super().__init__()
        self.reset_question()
        self.msg_prefix: str = "❔"

    def reset_question(self):
        self.current_question: int = -1
        self.current_answer: int = -1
        self.current_participants: dict = dict()  # {username:(correct, incorrect)}
        self.almost_active = False
        self.active = False
        self.answer_text = None

    @ModCommand(name, "trivia", permission="admin")
    async def trivia(self, msg, *args):
        print("trivia")

    # This command will almost always be sent by the webserver,
    # setting the CommandContext to Whisper will allow it in whispers
    # only, but when sent over the command console, context is ignored.
    @SubCommand(trivia, "q")  # , context=CommandContext.WHISPER) #TODO
    async def trivia_q(self, msg: Message, question_num: int, answer_num: int):
        question_num, answer_num = int(question_num), int(answer_num)  # Framework only passes strings, convert it.

        print(f"Trivia question #{question_num}, A:{answer_num}")

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
            await sleep(10)  # Sleep early to let the watchers catch up to the stream

            # Mark question as active
            self.active = True  # Resets in reset_question

            # Send the question to chat
            await msg.reply(f"{self.msg_prefix}{result.text}")
            await sleep(10)

            await msg.reply(f"{self.msg_prefix}15 seconds remaining")
            await sleep(10)
            await msg.reply(f"{self.msg_prefix}Final answers...")
            await sleep(5)
            await msg.reply(f"{self.msg_prefix}Answer: {self.answer_text.upper()}")

            self.reset_question()

    @SubCommand(trivia, "end")
    async def trivia_end(self, msg: Message):
        await msg.reply(f"{bot.msg_prefix} Thanks for playing BaldEngineer Trivia!")

    async def on_raw_message(self, msg: Message):
        if (
            self.current_question > 0 and msg.is_privmsg and self.active
        ):  # Check if trivia is active and not a server message

            normalized = msg.normalized_parts
            if len(normalized) == 1 and len(normalized[0]) == 1 and normalized[0] in ascii_lowercase:
                answer = normalized[0]
                if answer == self.answer_text:
                    await msg.reply("Correct!")
