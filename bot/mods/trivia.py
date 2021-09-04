import datetime
import json
import random
from asyncio import sleep
from string import ascii_lowercase
from string import ascii_uppercase

from main import bot
from mods._database import session
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.message import Message
from twitchbot.util import run_command
from twitchbot.util.twitch_api_util import get_user_id

from models import Settings
from models import TriviaQuestions
from models import TriviaResults
from models import Users


class TriviaModOld:  # (Mod):
    name = "triviamod"

    def __init__(self):
        super().__init__()
        self.reset_question()
        self.msg_prefix: str = "❔"
        # Create session for participant tracking
        self.session = dict()
        self.scoreboard = dict()
        self.topscores = dict()
        self.manual_delay: int = 7

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
        pass

    @SubCommand(trivia, "delay", permission="admin")
    async def delay(self, msg: Message, new_delay: int = None):
        """Adds a delay at the start of the next question"""
        if new_delay:
            self.manual_delay = int(new_delay)  # framework doesn't typecast
            await msg.reply(f"{self.msg_prefix}Flux Capacitor Trimmed to {self.manual_delay} seconds")
        else:
            await msg.reply(f"{self.msg_prefix}Flux capacitor currently calibrated to {self.manual_delay} seconds")

    @SubCommand(trivia, "q", permission="bot", hidden=True)  # , context=CommandContext.CONSOLE)
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
            if await sleep_if_active(self.manual_delay):
                # Send the question to chat
                await msg.reply(f"{self.msg_prefix}{result.text}")

            if await sleep_if_active(45):
                message_text = [
                    "Time is almost up",
                    "15 seconds remaining",
                    "0xF seconds remaining",
                    "0x10 seconds remaining",
                ]
                selected_message_text = random.choice(message_text)
                await msg.reply(f"{self.msg_prefix}{selected_message_text}")

            if await sleep_if_active(10):
                await msg.reply(f"{self.msg_prefix}Final answers...")

            # One last sleep to let people get final answers in.
            await sleep_if_active(5)

            # Insert/Update the participants that got a correct answer
            correctly_answered = list()
            for participant in self.session:
                if (
                    self.session[participant]["q"].get(self.current_question, False)
                    and participant in self.current_question_participant  # See note in reset_question
                ):
                    correctly_answered.append(participant)
                    # Get the user id, but sometimes this fails and returns a -1, if it's -1 try again up to 3 times.
                    # If it still fails, send a message to the console and do not insert into the database.
                    user_id = -1
                    get_user_id_count = 0
                    while user_id == -1:
                        user_id = await get_user_id(participant)
                        get_user_id_count += 1
                        if get_user_id_count >= 3:
                            print(f"Unable to fetch user id for {participant} after 3 attempts.")
                            break

                    query = (
                        session.query(TriviaResults)
                        .filter(TriviaResults.user_id == user_id, TriviaResults.channel == channel_id)
                        .one_or_none()
                    )  # Grab the current row
                    if query:  # Update it
                        query.trivia_points += 1
                        query.questions_answered_correctly[self.current_question] = True

                    else:
                        # Insert if the row didn't exist.
                        query = TriviaResults(
                            user_id=user_id,
                            channel=channel_id,
                            questions_answered_correctly={self.current_question: True},
                            trivia_points=1,
                        )
                        session.add(query)

                    # Update the database
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
        if len(self.topscores) == 0:
            # Trivia hasn't ended yet, force end it.
            await run_command("trivia", msg, ["end"], blocking=True)

        # Grab the channel ID, we'll need it later.
        channel_id = await get_user_id(msg.channel.name)

        first = self.topscores.popitem() if len(self.topscores) > 0 else None
        second = self.topscores.popitem() if len(self.topscores) > 0 else None
        third = self.topscores.popitem() if len(self.topscores) > 0 else None

        if third is not None:
            await msg.reply(f"{self.msg_prefix}In third place is {', '.join(third[1])} with {third[0]}")
            await sleep(5)

        if second is not None:
            await msg.reply(f"{self.msg_prefix}In second place is {', '.join(second[1])} with {second[0]}")
            await sleep(5)

        if first is not None:
            await msg.reply(f"{self.msg_prefix}In first place is {', '.join(first[1])} with {first[0]}")
            # await msg.reply(f"{bot.msg_prefix}Congratulations to all of the trivia winners.")

        # 203
        # Special announcements for first place winners
        if first is not None:  # No participants with correct answers
            winner_list = first[1]

            # Grab the ID numbers of all winners
            winner_ids = list()
            for winner in winner_list:
                # Grab winners stats
                winner_id = -1
                while winner_id == -1:
                    winner_id = await get_user_id(winner)

                winner_ids.append(winner_id)

            winner_db = (
                session.query(TriviaResults, Users)
                .filter(
                    TriviaResults.user_id.in_(winner_ids),
                    TriviaResults.channel == channel_id,
                    Users.user_id == TriviaResults.user_id,
                )
                .all()
            )

            # First win
            first_time_winner = list()
            win_count = dict()
            most_wins = 0
            for trivia, user in winner_db:
                # Used for first time winner
                if trivia.total_wins == 1:
                    first_time_winner.append(user.user)

                # Used for most wins and when multiple tie for most
                if trivia.total_wins > most_wins:
                    most_wins = trivia.total_wins

                # Create the list if it doesn't exist in the dictionary yet
                if not win_count.get(trivia.total_wins, False):
                    win_count[trivia.total_wins] = list()

                # Used for tracking how many wins each person has
                win_count[trivia.total_wins].append(user.user)

            # Send a final congratulations message
            if len(first_time_winner) > 0:  # First time winners
                await msg.reply(f"{self.msg_prefix}CONGRATULATIONS {', '.join(first_time_winner)} on your first win!!")
            elif len(win_count[most_wins]) > 1:  # Multiple top winners
                await msg.reply(f"{self.msg_prefix}Congrats to {', '.join(win_count[most_wins])} for the most wins!")
            elif len(win_count[most_wins]) == 1:  # Single top winner
                await msg.reply(f"{self.msg_prefix}Congrats to {win_count[most_wins][0]}, you have won {most_wins} times!")

        # Reset the topscores
        self.topscores = dict()

    @SubCommand(trivia, "end", permission="bot")
    async def trivia_end(self, msg: Message):

        # Will trigger interupting the current question.
        self.trivia_active = False

        # Give the bot just enough time to send the last message for the current question.
        await sleep(1)

        scoreboard = dict()

        # Assign the participant to how many they got correct on the scoreboard
        for participant in self.session:
            correct = self.session[participant]["correct"]
            if not scoreboard.get(correct, False):
                scoreboard[correct] = list()
            scoreboard[correct].append(participant)

        # Sort the scoreboard by score, lowest to highest so popitem can pull the bottom item
        scoreboard_order = sorted(scoreboard.keys(), key=lambda x: x)

        # Update the winners in the database
        if len(scoreboard_order) > 0:  # We have participants, update them
            # Grab channel ID for database insertion
            channel_id = await get_user_id(msg.channel.name)

            # Loop through the highest score as a winner
            for participant in scoreboard[scoreboard_order[0]]:

                # Get the user id, but sometimes this fails and returns a -1, if it's -1 try again up to 3 times.
                # If it still fails, send a message to the console and do not insert into the database.
                user_id = -1
                get_user_id_count = 0
                while user_id == -1:
                    user_id = await get_user_id(participant)
                    get_user_id_count += 1
                    if get_user_id_count >= 3:
                        print(f"Unable to fetch user id for {participant} after 3 attempts.")
                        break

                # User should have already been in the database from answering the question
                if (
                    session.query(TriviaResults)
                    .filter(TriviaResults.user_id == user_id, TriviaResults.channel == channel_id)
                    .update({TriviaResults.total_wins: TriviaResults.total_wins + 1})
                ):
                    session.commit()

        # Sort the scoreboard and save it
        self.topscores = dict()
        for order_id in scoreboard_order:
            self.topscores[order_id] = scoreboard[order_id]

        # Clear the session data
        self.session = dict()

        await msg.reply(
            f"{bot.msg_prefix}Thank you for playing trivia! Stick around, @baldengineer will share the winners soon!"
        )

    async def on_raw_message(self, msg: Message):
        if (
            self.current_question > 0 and msg.is_privmsg and self.question_active
        ):  # Check if trivia is active and not a server message

            normalized: tuple = msg.normalized_parts
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
                self.current_question_participant.add(author)  # See note in reset_question

                # Check if user has already provided an answer, only first answer accepted
                if not self.session[author].get(self.current_question, False):
                    if answer == self.answer_text:  # Correct answer
                        self.session[author]["q"][self.current_question] = True
                        self.session[author]["correct"] += 1
                    else:  # Incorrect
                        self.session[author]["q"][self.current_question] = False
                        self.session[author]["incorrect"] += 1

    async def update_scoreboard_mqtt(self):
        """Update the scoreboard mqtt topic"""

        pass


class TriviaMod(Mod):
    name = "triviamod"

    def __init__(self):
        super().__init__()
        self.msg_prefix: str = "❔"
        self.trivia_active = False
        self.active_question = None
        self.active_answer = None
        self.ready_for_answers = False
        self.answered_active_question = dict()
        self.current_question_answers = dict()
        self.scoreboard = dict()
        self.questions_into_trivia = 0

        # Read the set delay from the db, or default to 7 seconds if not set
        self.trivia_delay_key = "trivia_delay"
        query = session.query(Settings).filter(Settings.key == self.trivia_delay_key).one_or_none()
        self.question_delay = int(query.value) if query else 7

    @ModCommand(name, "trivia", permission="admin")
    async def trivia(self, msg, *args):
        pass

    @SubCommand(trivia, "run_question", permission="bot", hidden=True)
    async def trivia_run_question(self, msg: Message, question_num: int, answer_num: int):
        question_num, answer_num = int(question_num), int(answer_num)  # Framework only passes strings, convert it.

        # Don't send a question while another is active
        # This will only prevent the next question from starting
        # not multiple sent at the same time
        while self.active_question:
            await sleep(0.5)

        print(f"Trivia question #{question_num}, Answer: {ascii_lowercase[answer_num-1].upper()}")

        self.active_question = session.query(TriviaQuestions).filter_by(id=question_num).one_or_none()

        # Save the answer letter for score checking
        self.active_answer = ascii_lowercase[answer_num - 1]

        if self.active_question is not None:
            self.started_at = datetime.datetime.now()
            last_timer_message_sent = 0

            # Send a welcome message and instructions if this is the first question of the session
            if not self.trivia_active:
                await msg.reply(f"{bot.msg_prefix}Trivia incoming...")
                await msg.reply(
                    f"{self.msg_prefix}To play trivia, answer with a single letter message of your answer(case insensitive)."
                )
                self.trivia_active = True

            # How many questions into trivia are we
            self.questions_into_trivia += 1

            # How many answers are there for this question
            self.num_of_answers = len(json.loads(self.active_question.answers))
            # Build MQTT topic trivia_current_question_answers_setup
            answers = list()
            for idx in range(self.num_of_answers):
                answers.append(ascii_uppercase[idx])

            mqtt_answers_setup = {
                "title": "Choose your answer",
                "total_duration": 59,
                "choices": answers,
                "active": True,
            }
            # Send the setup data
            await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_answers_setup, mqtt_answers_setup, retain=True)
            await bot.MQTT.send(bot.MQTT.Topics.trivia_question, self.active_question.text)
            await bot.MQTT.send(bot.MQTT.Topics.trivia_answers, self.active_question.answers)

            def check_send_time(seconds_into_trivia: int):
                return (
                    self.started_at
                    + datetime.timedelta(seconds=self.question_delay)
                    + datetime.timedelta(seconds=seconds_into_trivia)
                ) < datetime.datetime.now()

            while self.active_question:
                if last_timer_message_sent == 0 and check_send_time(0):  # Message 1
                    # Send the question to chat
                    self.ready_for_answers = True
                    await msg.reply(f"{self.msg_prefix}{self.active_question.text}")
                    ic(f"{datetime.datetime.now() - self.started_at} seconds into question.")

                    last_timer_message_sent += 1

                elif last_timer_message_sent == 1 and check_send_time(10):
                    ic(f"{datetime.datetime.now() - self.started_at} seconds into question.")
                    last_timer_message_sent += 1

                elif last_timer_message_sent == 2 and check_send_time(20):
                    ic(f"{datetime.datetime.now() - self.started_at} seconds into question.")
                    last_timer_message_sent += 1
                elif last_timer_message_sent == 3 and check_send_time(30):
                    ic(f"{datetime.datetime.now() - self.started_at} seconds into question.")
                    last_timer_message_sent += 1
                elif last_timer_message_sent == 4 and check_send_time(40):
                    ic(f"{datetime.datetime.now() - self.started_at} seconds into question.")
                    last_timer_message_sent += 1

                elif last_timer_message_sent == 5 and check_send_time(44):  # Message 2
                    message_text = [
                        "Time is almost up",
                        "15 seconds remaining",
                        "0xF seconds remaining",
                        "0x10 seconds remaining",
                    ]
                    selected_message_text = random.choice(message_text)
                    await msg.reply(f"{self.msg_prefix}{selected_message_text}")

                    last_timer_message_sent += 1

                elif last_timer_message_sent == 6 and check_send_time(50):
                    ic(f"{datetime.datetime.now() - self.started_at} seconds into question.")
                    last_timer_message_sent += 1

                elif last_timer_message_sent == 7 and check_send_time(54):  # Message 3
                    await msg.reply(f"{self.msg_prefix}Final answers...")

                    last_timer_message_sent += 1

                elif last_timer_message_sent == 8 and check_send_time(60):  # Message 4
                    # All scoring is done elsewhere
                    self.active_question = None  # End the question
                    self.active_answer = None
                    self.started_at = datetime.datetime.max
                    self.ready_for_answers = False

                else:
                    await sleep(0.25)  # Do an asyncio sleep to let other things run while we wait

            ic("Trivia question ended")

            # Build a list of people that got the answer correct
            correct_list = list()
            for author, correct in self.answered_active_question.items():
                if correct:
                    correct_list.append(author)

            if correct_list:
                msg_names = ", ".join(correct_list)
                message = f"{self.msg_prefix} Congrats to {msg_names} for the correct answer."
                if len(message) > 500:
                    count = len(msg_names.split(", "))
                    message = f"{self.msg_prefix} Wow! {count} of you got it right! Congrats"

            else:
                message = f"{self.msg_prefix}Hmm... on to question number next!"

            await msg.reply(message)
            await bot.MQTT.send(bot.MQTT.Topics.trivia_leaderboard, self.calculate_scoreboard())

            # Wipe the current answers display
            await bot.MQTT.send(
                bot.MQTT.Topics.trivia_current_question_answers_data, {"votes": self.current_question_answers, "done": True}
            )
            self.current_question_answers = dict()

            # Clear the dict of who answered
            self.answered_active_question = dict()

            await sleep(5)
            await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_answers_data, {})
            await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_answers_setup, {"active": False})

    @SubCommand(trivia, "delay", permission="admin")
    async def trivia_delay(self, msg: Message, new_delay: int = None):
        """Adds a delay at the start of the next question"""
        if new_delay:
            self.question_delay = int(new_delay)  # framework doesn't typecast

            # Update delay in database, or insert if key doesn't exist.
            query = session.query(Settings).filter(Settings.key == self.trivia_delay_key).one_or_none()
            if query:
                query.value = new_delay
                session.commit()
            else:
                query = Settings(key=self.trivia_delay_key, value=new_delay)
                session.add(query)
                session.commit()

            await msg.reply(f"{self.msg_prefix}Flux Capacitor Trimmed to {self.question_delay} seconds")
        else:
            await msg.reply(f"{self.msg_prefix}Flux capacitor currently calibrated to {self.question_delay} seconds")

    @SubCommand(trivia, "end", permission="bot")
    async def trivia_end(self, msg: Message):

        self.trivia_active = False  # Deactivate trivia, allows winner to run

        # Clears the current question, interrupting the timer loop for it
        self.active_question = None

        self.questions_into_trivia = 0

        # Give the bot just enough time to send the last message for the current question.
        await sleep(1)

        await msg.reply(
            f"{bot.msg_prefix}Thank you for playing trivia! Stick around, @baldengineer will share the winners soon!"
        )

    @SubCommand(trivia, "winner", permission="admin")
    async def trivia_winner(self, msg: Message):
        """Sends the winners to chat, also clearing the scoreboard"""

        if self.trivia_active:
            # Trivia hasn't ended yet, force end it.
            await run_command("trivia", msg, ["end"], blocking=True)

        winners = self.calculate_winner()
        how_many_winners = len(winners)

        # places = ["first", "second", "third"]
        places = ["third", "second", "first"]

        messages = list()  # Store for the messages to send
        for pl in range(how_many_winners):
            # Negative length of winners + current range number, used to count backwards in the places list
            place = -how_many_winners + pl
            winner = winners.pop()
            ic(winner, places[place])
            messages.append(f"{self.msg_prefix} In {places[place]} is {winner[0]} with {winner[1]} points.")

        # Send leaderboard to MQTT
        await bot.MQTT.send(bot.MQTT.Topics.trivia_leaderboard, self.scoreboard, retain=True)

        for idx in range(len(messages)):
            # Send the congratulatory messages with a delay between them
            await msg.reply(messages[idx])
            await sleep(5)

        # Clear the scoreboard for the next session
        self.scoreboard = dict()

        # Clear the trivia related MQTT topics
        await sleep(5)
        await bot.MQTT.send(bot.MQTT.Topics.trivia_leaderboard, None)
        await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_answers_setup, None)
        await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_answers_data, None)

    async def on_privmsg_received(self, msg: Message):
        if (
            self.active_question and self.ready_for_answers and msg.is_privmsg
        ):  # Check if trivia is active and not a server message
            normalized: tuple = msg.normalized_parts  # Normalize converts all words in message to lowercase
            if len(normalized) == 1 and len(normalized[0]) == 1 and normalized[0] in ascii_lowercase:
                answer = normalized[0]

                if (
                    msg.author not in self.answered_active_question.keys()  # Make sure the user hasn't already answered
                    and answer in ascii_lowercase[: self.num_of_answers]  # Make sure answer is a valid one
                ):
                    # Increment the counter for the answer given, and send to MQTT
                    ascii_index = str(ascii_lowercase.index(answer) + 1)
                    self.current_question_answers[ascii_index] = self.current_question_answers.get(ascii_index, 0) + 1
                    await bot.MQTT.send(  # {"seconds_left": 4.5, "votes": {"1": 1, "2": 2, "3": 3}, "done": false}
                        bot.MQTT.Topics.trivia_current_question_answers_data,
                        {"votes": self.current_question_answers, "done": False},
                    )

                if answer == self.active_answer and msg.author not in self.answered_active_question.keys():
                    add_to_score = self.calculate_points_for_question()
                    _ = f"{msg.author} awarded {add_to_score} points"
                    ic(_)

                    self.scoreboard[msg.author] = self.scoreboard.get(msg.author, 0) + add_to_score
                    self.answered_active_question[msg.author] = True

                elif msg.author not in self.answered_active_question.keys():
                    self.answered_active_question[msg.author] = False

    def calculate_points_for_question(self):
        """Calculates and returns the score for the user, will always return a minimum of 5 points"""

        now = datetime.datetime.now()
        if self.started_at:
            adjusted_start = self.started_at + datetime.timedelta(seconds=self.question_delay)
        else:
            return 5

        if now - adjusted_start < datetime.timedelta(seconds=60):
            seconds = datetime.timedelta(seconds=60) - (now - adjusted_start)
            score = int(seconds.total_seconds() * 1)
            score = score if score > 5 else 5
            score = score * self.questions_into_trivia
        else:
            # Just in case the answer comes in before the delay expires, max out the score
            score = 60 * self.questions_into_trivia

        return score

    def calculate_winner(self):
        ordered_scoreboard = {k: v for k, v in sorted(self.scoreboard.items(), key=lambda item: item[1])}
        top_three = list()
        num = len(ordered_scoreboard) if len(ordered_scoreboard) < 3 else 3
        for _ in range(num):
            top_three.append(ordered_scoreboard.popitem())

        return top_three

    def calculate_scoreboard(self):
        ordered_scoreboard = {k: v for k, v in sorted(self.scoreboard.items(), key=lambda item: item[1])}
        return ordered_scoreboard

    async def update_player_scores(self):
        """Write the player scores to the database"""
        pass
