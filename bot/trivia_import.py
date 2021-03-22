import json
from datetime import date

from mods._database import session

from models import Trivia


with open("questions.txt") as file:
    questions = json.loads(file.read())
    questions = questions["quiz"]


for key, values in questions.items():
    query_result = session.query(Trivia).filter(Trivia.id == int(key)).one_or_none()
    if query_result is None:
        try:
            insert = Trivia(
                id=int(key),
                text=values["text"],
                answers=json.dumps(values["answers"]),
                explain=values["explain"],
                last_used_date=date.fromisoformat(values["last_used_date"]) if values["last_used_date"] != "" else date.min,
                created_date=date.fromisoformat(values["created_date"]) if values["created_date"] != "" else date.min,
                created_by=values["created_by"],
                reference=values["reference"],
            )
            session.add(insert)
            session.commit()
            print(f"Trivia question #{key} inserted.")

        except KeyError as e:
            print(f"Missing value for {e.args[0]}")

    elif query_result.text != values["text"]:
        print(f"Question #{key} question text does not match database.")

print("Trivia update complete...")
