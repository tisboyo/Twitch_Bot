# Added for #152
from asyncio import sleep

from main import bot
from mods._database import session
from twitchbot import cfg
from twitchbot import Channel
from twitchbot import channels
from twitchbot import CommandContext
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.message import Message

from models import Settings
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

    @ModCommand(name, "trivia", permission="admin")
    async def trivia(self, msg, *args):
        print("trivia")

    # This command will almost always be sent by the webserver,
    # setting the CommandContext to Whisper will allow it in whispers
    # only, but when sent over the command console, context is ignored.
    @SubCommand(trivia, "q")  # , context=CommandContext.WHISPER) #TODO
    async def trivia_q(self, msg: Message, question_num: int, answer_num: int):
        question_num, answer_num = int(question_num), int(answer_num)  # Framework only passes strings, convert it.
        self.current_question = question_num
        self.current_answer = answer_num

        result = session.query(TriviaQuestions).filter_by(id=self.current_question).one_or_none()

        if result is not None:
            await msg.reply(f"{self.msg_prefix}{result.text}")
            await sleep(10)
            await msg.reply(f"{self.msg_prefix}15 seconds remaining")
            await sleep(10)
            await msg.reply(f"{self.msg_prefix}Final answers...")
            await sleep(5)
            await msg.reply(f"{self.msg_prefix}Answer: A")

            self.reset_question()

    async def on_raw_message(self, msg: Message):
        if self.current_question > 0 and msg.is_privmsg:  # Check if trivia is active and not a server message
            print(msg)
