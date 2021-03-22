# Created for #151
import json
from datetime import datetime
from typing import Union

from mods._database import session

from models import Trivia


with open("questions.txt") as file:
    questions = json.loads(file.read())
    questions = questions["quiz"]


for id_num, values in questions.items():
    try:
        # Format the question data so the database can handle it.
        question_data: dict = dict(  # Intentionally excluding id from this to prevent changing it accidentally
            text=values["text"],
            answers=json.dumps(values["answers"]),
            explain=values["explain"],
            last_used_date=datetime.fromisoformat(values["last_used_date"])
            if values["last_used_date"] != ""
            else datetime.min,
            last_update_date=datetime.today(),
            created_date=datetime.fromisoformat(values["created_date"]) if values["created_date"] != "" else datetime.min,
            created_by=values["created_by"],
            reference=values["reference"],
        )
    except KeyError as e:
        print(f"Missing value for {e.args[0]} for question #{id_num}")
        continue

    # Read the current database for this id
    query_result: Union[Trivia, None] = session.query(Trivia).filter_by(id=int(id_num)).one_or_none()

    if query_result is None:
        # Insert the question into the database
        insert = Trivia(id=int(id_num), **question_data)
        session.add(insert)
        session.commit()
        print(f"Trivia question #{id_num} inserted.")

    elif query_result.text != values["text"] and not values.get("force_update", False):
        # Output a message if question text does not match and force_update is not True
        print(f"Question #{id_num} text does not match database. Not updating it. Add force_update=true to force.")

    else:
        # Check if force update flag is set, if so warn the console
        if values.get("force_update", False):
            print(f"Question #{id_num} is set to force update. You should remove that.")

        if (  # Update the questions data if it has changed
            values.get("force_update", False)
            or query_result.answers != question_data["answers"]
            or query_result.last_used_date != question_data["last_used_date"]
            or query_result.reference != question_data["reference"]
            or query_result.explain != question_data["explain"]
        ):
            results = session.query(Trivia).filter_by(id=id_num).update(question_data)
            session.commit()
            print(f"Question #{id_num} updated.")


print("Trivia update complete...")
