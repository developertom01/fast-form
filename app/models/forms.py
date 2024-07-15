from pydantic import BaseModel
from typing import Iterable
from aiosqlite import Row
import humanize
from datetime import datetime


class FormQuestion(BaseModel):
    id: str
    question: str
    type: str
    required: bool
    choices: list[str] | None = None


class Form(BaseModel):
    id: str
    title: str
    description: str | None = None
    published_at: str | None = None
    created_at: str
    questions: list[FormQuestion] | None = None

    @staticmethod
    def parse_rows(rows: Iterable[Row]):
        data: list[Form] = []
        count = 0

        for row in rows:
            count = row[0]
            data.append(
                Form(
                    id=row[1],
                    title=row[2],
                    description=row[3],
                    published_at=get_published_at_formatted(row[5]),
                    created_at=humanize.naturaltime(datetime.fromisoformat(row[6])),
                )
            )

        return data, count

    def parse_joined_single(rows: Iterable[Row]):
        form = {}
        for row in rows:
            form["id"] = row[0]
            form["title"] = row[1]
            form["description"] = row[2]
            form["published_at"] = get_published_at_formatted(row[4])
            form["created_at"] = get_published_at_formatted(row[5])

            if "questions" not in form:
                form["questions"] = {}

            question_id = row[6]
            if question_id not in form["questions"]:
                form["questions"][question_id] = {}
            if row[8] == "choice" and "choices" not in form["questions"][question_id]:
                form["questions"][question_id]["choices"] = []
            elif row[8] != "choice":
                form["questions"][question_id]["choices"] = None

            form["questions"][question_id]["id"] = row[6]
            form["questions"][question_id]["question"] = row[7]
            form["questions"][question_id]["type"] = row[8]
            form["questions"][question_id]["required"] = bool(row[9])
            if isinstance(form["questions"][question_id]["choices"], list):
                form["questions"][question_id]["choices"].append(row[10])

        form_model = Form(
            id=form["id"],
            title=form["title"],
            description=form["description"],
            published_at=form["published_at"],
            created_at=form["created_at"],
            questions=[],
        )

        for q in form["questions"].values():
            question = FormQuestion(
                id=q["id"],
                question=q["question"],
                type=q["type"],
                required=q["required"],
                choices=q["choices"],
            )
            form_model.questions.append(question)

        return form_model


def get_published_at_formatted(published_at: str | None):
    return (
        humanize.naturaltime(datetime.fromisoformat(published_at))
        if published_at is not None
        else "Not Published"
    )
