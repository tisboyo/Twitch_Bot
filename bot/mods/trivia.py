import datetime
import json
import random
from asyncio import sleep
from string import ascii_lowercase
from string import ascii_uppercase

from main import bot
from mods._database import session
from sqlalchemy import func
from twitchbot import cfg
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
        self.question_points = dict()
        self.current_question_answers_count = dict()
        self.scoreboard = dict()
        self.questions_into_trivia = 0
        self.started_at = datetime.datetime.max
        self.start_running = False

        # Read the set delay from the db, or default to 7 seconds if not set
        self.trivia_delay_key = "trivia_delay"
        query = session.query(Settings).filter(Settings.key == self.trivia_delay_key).one_or_none()
        self.question_delay = int(query.value) if query else 7

    async def on_connected(self):
        # Deactivate on startup, just in case of a crash
        await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_setup, {"active": False}, retain=True)

    @ModCommand(name, "trivia", permission="admin")
    async def trivia(self, msg, *args):
        pass

    @SubCommand(trivia, "run_question", permission="bot", hidden=True)
    async def trivia_run_question(self, msg: Message, question_num: int):
        def check_send_time(seconds_into_trivia: int):
            return (
                self.started_at
                + datetime.timedelta(seconds=self.question_delay)
                + datetime.timedelta(seconds=seconds_into_trivia)
            ) < datetime.datetime.now()

        question_num = int(question_num)  # Framework only passes strings, convert it.

        # Don't send a question while another is active
        # This will only prevent the next question from starting
        # not multiple sent at the same time
        while self.active_question:
            await sleep(0.5)

        self.active_question = session.query(TriviaQuestions).filter_by(id=question_num).one_or_none()

        if self.active_question is not None:
            # Randomize answers, generate a new number order of indexes
            ans = json.loads(self.active_question.answers)
            ln = len(ans)
            new_order = [idx for idx in range(1, ln + 1)]
            random.shuffle(new_order)

            # Assign the new random indexes to the question text
            randomized_answers = dict()
            temp_counter = 0
            for k in ans:
                randomized_answers[str(new_order[temp_counter])] = ans[k]
                temp_counter += 1

            # Grab the correct answer from the new order
            for a in randomized_answers:
                if bool(randomized_answers[a]["is_answer"]):
                    self.active_answer = int(a) - 1
                    break

            print(f"Trivia question #{question_num}, Answer: {ascii_lowercase[self.active_answer].upper()}")

            # Update the question last used
            self.active_question.last_used_date = datetime.date.today()
            session.commit()

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
            # Build MQTT topic trivia_current_question_setup
            answers_choices = list()
            for idx in range(self.num_of_answers):
                # Parenthesis inside the f string is sent to the trivia page to format it
                answers_choices.append(f"{ascii_uppercase[idx]})")

            # Pad out the answer_choices so the spacing on the trivia display displays correctly
            min_number_of_questions_to_send = 4
            while len(answers_choices) < min_number_of_questions_to_send:
                answers_choices.append("")

            mqtt_question_setup = {
                "id": self.active_question.id,
                "text": self.active_question.text,
                "total_duration": 59,
                "choices": answers_choices,
                "answers": randomized_answers,
                "image": self.active_question.id if self.active_question.image is None else self.active_question.image,
                "sound": self.active_question.id if self.active_question.sound is None else self.active_question.sound,
                "active": True,
            }
            # Pad out the answers if there are less than 4 so the spacing is correct on the front end
            if len(mqtt_question_setup["answers"]) < min_number_of_questions_to_send:
                for idx in range(len(mqtt_question_setup["answers"]) + 1, min_number_of_questions_to_send + 1):
                    mqtt_question_setup["answers"][str(idx)] = {"is_answer": 0, "text": ""}

            # Send the setup data
            await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_setup, mqtt_question_setup, retain=True)
            await bot.MQTT.send(bot.MQTT.Topics.trivia_question, self.active_question.text)
            await bot.MQTT.send(bot.MQTT.Topics.trivia_answers, self.active_question.answers)

            exp_choices = ["AddOhms: 🤖 Thanks for playing!", "Wizard James: 🧙‍♂️ Thanks for playing!"]
            explanation = (
                self.active_question.explain if self.active_question.explain is not None else random.choice(exp_choices)
            )  # Save this to send with the closing mqtt

            while self.active_question:
                if last_timer_message_sent == 0 and check_send_time(0):  # Message 1
                    # Send the question to chat
                    self.ready_for_answers = True
                    await msg.reply(f"{self.msg_prefix}{self.active_question.text}")
                    ic(f"{datetime.datetime.now() - self.started_at} seconds into question.")

                    last_timer_message_sent += 1

                elif last_timer_message_sent == 1 and check_send_time(44):  # Message 2
                    message_text = [
                        "Time is almost up",
                        "15 seconds remaining",
                        "0xF seconds remaining",
                        "0x10 seconds remaining",
                    ]
                    selected_message_text = random.choice(message_text)
                    await msg.reply(f"{self.msg_prefix}{selected_message_text}")

                    last_timer_message_sent += 1

                elif last_timer_message_sent == 2 and check_send_time(54):  # Message 3
                    await msg.reply(f"{self.msg_prefix}Final answers...")

                    last_timer_message_sent += 1

                elif last_timer_message_sent == 3 and check_send_time(60):  # Message 4
                    # All scoring is done elsewhere
                    self.active_question = None  # End the question
                    # self.active_answer = None
                    self.started_at = datetime.datetime.max
                    self.ready_for_answers = False

                else:
                    await self.send_answers_to_mqtt()
                    await sleep(0.25)  # Do an asyncio sleep to let other things run while we wait

            ic("Trivia question ended")

            """################### self.active_question has been cleared ####################"""

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

            # Send the current answer status to MQTT
            # Always send answer_id when done = True otherwise the front end will puke
            await self.send_answers_to_mqtt(done=True, explanation=explanation, answer_id=self.active_answer + 1)

            await self.update_users_in_database(question_num)

            self.current_question_answers_count = dict()

            # Clear the dict of who answered, and their points
            self.answered_active_question = dict()
            self.question_points = dict()

            await sleep(5)
            await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_setup, {"active": False}, retain=True)

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

    @SubCommand(trivia, "start", permission="bot")
    async def trivia_start(self, msg: Message, debug=False):
        ic("!trivia start command run")
        if self.start_running:
            return

        self.start_running = True

        debug = bool(int(debug))

        while self.start_running:
            if self.active_question:
                # There is already a question active, lets not start another one.
                sleep(0.25)

            if not debug:
                question = (
                    session.query(TriviaQuestions)
                    .filter(
                        TriviaQuestions.last_used_date < datetime.date.today(), TriviaQuestions.enabled == True  # noqa:E712
                    )
                    .order_by(func.random())
                    .limit(1)
                    .one_or_none()
                )
            else:
                question = (
                    session.query(TriviaQuestions)
                    .filter(TriviaQuestions.enabled == True)  # noqa:E712
                    .order_by(func.random())
                    .limit(1)
                    .one_or_none()
                )

            if not question:  # The query returned None
                print("We have used all of the trivia questions today!")
                await bot.MQTT.send(
                    bot.MQTT.Topics.trivia_current_question_setup,
                    {
                        "text": "We've used ALL of the trivia questions today.",
                        "choices": [],
                        "answers": {},
                        "id": "error",
                        "active": True,
                        "image": 0,
                        "sound": 0,
                        "explain": "Send your trivia suggestions in discord!",
                    },
                    retain=True,
                )
                self.trivia_active = False
                sleep(5)
                break

            # Run the question
            await run_command("trivia", msg, ["run_question", str(question.id)], blocking=True)
            await sleep(1)
            await bot.MQTT.send(
                bot.MQTT.Topics.trivia_current_question_setup,
                {
                    "text": "New trivia preview!",
                    "choices": [],
                    "answers": {},
                    "id": "default",
                    "active": True,
                    "image": 0,
                    "sound": 0,
                    "explain": "Send your trivia suggestions in discord!",
                },
                retain=True,
            )
            await sleep(2)
            await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_setup, {"active": False}, retain=True)
            await sleep(2)

        self.start_running = False

    @SubCommand(trivia, "end", permission="bot")
    async def trivia_end(self, msg: Message):

        self.trivia_active = False  # Deactivate trivia, allows winner to run
        self.start_running = False
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

        channel_id = await self.get_user_id_with_retry(msg.channel.name)

        winners = self.calculate_winner()
        how_many_winners = len(winners)

        # Update winners in database
        await self.update_users_in_database(final=winners)

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

        how_many_messages = len(messages)
        for idx in range(how_many_messages):
            # Send the congratulatory messages with a delay between them
            await msg.reply(messages[idx])
            if idx < how_many_messages - 1:
                await sleep(5)

        # 203
        # Special announcements for first place winners
        if how_many_winners > 0:  # No participants with correct answers
            calc_winners = self.calculate_winner()
            high_score = calc_winners[0][1]

            winners = list()
            for participant, score in calc_winners:
                if score == high_score:
                    winners.append(participant)

            # Grab the ID numbers of all winners
            winner_ids = list()
            for winner in winners:
                # Grab winners stats
                winner_id = -1
                while winner_id == -1:
                    winner_id = await self.get_user_id_with_retry(winner)

                winner_ids.append(int(winner_id))

            winner_db = (
                session.query(TriviaResults, Users)
                .filter(
                    TriviaResults.user_id.in_(winner_ids),
                    TriviaResults.channel == channel_id,
                    Users.user_id == TriviaResults.user_id,
                    Users.channel == TriviaResults.channel,
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
            if first_time_winner:  # First time winners
                await msg.reply(f"{self.msg_prefix}CONGRATULATIONS {', '.join(first_time_winner)} on your first win!!")
            elif len(win_count[most_wins]) > 1:  # Multiple top winners
                await msg.reply(f"{self.msg_prefix}Congrats to {', '.join(win_count[most_wins])} for the most wins!")
            elif len(win_count[most_wins]) == 1:  # Single top winner
                await msg.reply(f"{self.msg_prefix}Congrats to {win_count[most_wins][0]}, you have won {most_wins} times!")

        # Clear the scoreboard for the next session
        self.scoreboard = dict()

        # Clear the trivia related MQTT topics
        await sleep(5)
        await bot.MQTT.send(bot.MQTT.Topics.trivia_leaderboard, None)
        await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_setup, None)
        await bot.MQTT.send(bot.MQTT.Topics.trivia_current_question_data, None)

    async def on_privmsg_received(self, msg: Message):
        if (
            self.active_question and self.ready_for_answers and msg.is_privmsg
        ):  # Check if trivia is active and not a server message
            normalized: tuple = msg.normalized_parts  # Normalize converts all words in message to lowercase
            # If the message has a length of 1 word, and that one word is 1 letter, and is in ascii_lowercase
            if len(normalized) == 1 and len(normalized[0]) == 1 and normalized[0] in ascii_lowercase:
                answer = normalized[0]

                # Update the points for the question, and send the total counts to MQTT
                if (  # If the answer is a valid one, and the author hasn't answered yet
                    answer in ascii_lowercase[: self.num_of_answers]
                    and msg.author not in self.answered_active_question.keys()
                ):
                    correct: bool = answer == ascii_lowercase[self.active_answer]  # Did they have the correct answer?

                    self.question_points[msg.author] = self.calculate_points_for_question(correct)
                    _ = f"{msg.author} awarded {self.question_points[msg.author]} points"
                    ic(_)

                    # Update the overall scoreboard
                    self.scoreboard[msg.author] = self.scoreboard.get(msg.author, 0) + self.question_points[msg.author]
                    self.answered_active_question[msg.author] = correct

                    # Increment the counter for the answer given, and send to MQTT
                    ascii_index = str(ascii_lowercase.index(answer) + 1)
                    self.current_question_answers_count[ascii_index] = (
                        self.current_question_answers_count.get(ascii_index, 0) + 1
                    )

                    # Send the current answer status to MQTT
                    await self.send_answers_to_mqtt()
                else:
                    # Completely ignore any input that wasn't valid for an answer, it was probably just chatting
                    pass

    def calculate_points_for_question(self, correct: bool):
        """Calculates and returns the score for the user, will always return a minimum of 5 points"""

        if correct:
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
        else:
            score = 1

        return score

    def calculate_winner(self) -> list:
        ordered_scoreboard = {k: v for k, v in sorted(self.scoreboard.items(), key=lambda item: item[1])}
        top_three = list()
        num = len(ordered_scoreboard) if len(ordered_scoreboard) < 3 else 3
        for _ in range(num):
            top_three.append(ordered_scoreboard.popitem())

        return top_three

    def calculate_scoreboard(self):
        ordered_scoreboard = {k: v for k, v in sorted(self.scoreboard.items(), key=lambda item: item[1])}
        return ordered_scoreboard

    async def send_answers_to_mqtt(self, done: bool = False, explanation: str = None, answer_id=None):

        # Track the total number of votes so we can send it to the front end
        total_votes = 0
        for k, v in self.current_question_answers_count.items():
            total_votes += v

        time_left = datetime.timedelta(seconds=60) - (datetime.datetime.now() - self.started_at)
        if time_left < datetime.timedelta(seconds=0):
            time_left = datetime.timedelta(seconds=0)

        message = {
            "votes": self.current_question_answers_count,
            "total": total_votes,
            "seconds_left": time_left.seconds,
            "done": done,
        }
        if explanation:
            message["explain"] = explanation
        if answer_id:
            message["answer_id"] = answer_id

        await bot.MQTT.send(
            bot.MQTT.Topics.trivia_current_question_data,
            message,
            retain=True,
        )

    async def update_users_in_database(self, question_id: int = 0, final: list = []) -> bool:
        # Insert/Update the participants that got a correct answer
        question_scores = self.question_points
        participants_correct = self.answered_active_question

        channel_id = await self.get_user_id_with_retry(cfg.channels[0])

        if question_id:  # Update an individual question
            combined = dict()
            for p in question_scores:
                combined[p] = dict()
                combined[p]["score"] = question_scores[p]
                combined[p]["correct"] = participants_correct[p]

                for participant, values in combined.items():
                    score, correct = values.values()

                    user_id = await self.get_user_id_with_retry(participant)

                    query = (
                        session.query(TriviaResults)
                        .filter(TriviaResults.user_id == user_id, TriviaResults.channel == channel_id)
                        .one_or_none()
                    )  # Grab the current row
                    if query:  # Update it
                        query.trivia_points += score
                        query.questions_answered_correctly[question_id] = correct

                    else:
                        # Insert if the row didn't exist.
                        query = TriviaResults(
                            user_id=user_id,
                            channel=channel_id,
                            questions_answered_correctly={question_id: correct},
                            trivia_points=1,
                        )
                        session.add(query)
        elif final:  # Update who won overall
            calc_winners = self.calculate_winner()
            high_score = calc_winners[0][1]

            winners = list()
            for participant, score in calc_winners:
                if score == high_score:
                    winners.append(participant)

            # Hopefully the user was in the bot's cache already and we don't have to do the multiple queries
            winner_ids = list()
            for winner in winners:
                winner_ids.append(await self.get_user_id_with_retry(winner))

            query = (
                session.query(TriviaResults)
                .filter(TriviaResults.user_id.in_(winner_ids), TriviaResults.channel == channel_id)
                .all()
            )  # Grab the current row
            if query:  # Update it
                for res in query:
                    res.total_wins += 1

            else:
                # Insert if the row didn't exist.
                # Not sure how they wouldn't exist at this point, but just in case.
                query = TriviaResults(
                    user_id=user_id,
                    channel=channel_id,
                    total_wins=1,
                )
                session.add(query)
        else:
            # Can happen if !trivia winner is run with no winners
            ic("update_users_in_database called without any parameters")
            return False

        # Update the database
        session.commit()

        return True

    async def get_user_id_with_retry(self, username: str):

        # Get the user id, but sometimes this fails and returns a -1, if it's -1 try again up to 3 times.
        # If it still fails, send a message to the console and do not insert into the database.
        user_id = -1
        get_user_id_count = 0
        while user_id == -1:
            user_id = await get_user_id(username)
            get_user_id_count += 1
            if get_user_id_count >= 3:
                print(f"Unable to fetch user id for {username} after 3 attempts.")
                return False

        return int(user_id)
