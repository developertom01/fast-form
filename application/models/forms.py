from pydantic import BaseModel
from typing import Iterable
from aiosqlite import Row


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
    create_at: str
    questions: list[FormQuestion] | None = None

    @staticmethod
    def parse_rows(rows: Iterable[Row]):
        data = {}
        count = 0

        for row in rows:
            count = row[0]
            form_id = row[1]
            form_title = row[2]
            form_description = row[3]
            form_published_at = row[4]
            form_created_at = row[5]
            question_id = row[6]
            question_question = row[7]
            question_type = row[8]
            required = row[9]
            question_choice = row[12]

            if form_id not in data:
                data[form_id] = {}

            data[form_id]["id"] = form_id
            data[form_id]["title"] = form_title
            data[form_id]["description"] = form_description
            data[form_id]["published_at"] = form_published_at
            data[form_id]["created_at"] = form_created_at

            if "questions" not in data[form_id]:
                data[form_id]["questions"] = {}

            if question_id not in data[form_id]["questions"]:
                data[form_id]["questions"][question_id] = {}

            data[form_id]["questions"][question_id]["id"] = question_id
            data[form_id]["questions"][question_id]["type"] = question_type
            data[form_id]["questions"][question_id]["question"] = question_question
            data[form_id]["questions"][question_id]["required"] = bool(required)

            if "choices" not in data[form_id]["questions"][question_id]:
                data[form_id]["questions"][question_id]["choices"] = []

            if question_choice is not None:
                data[form_id]["questions"][question_id]["choices"].append(question_choice)


        form_list:list[Form] = []
        for f in list(data.values()):
            form: Form = Form(
                id=f["id"],
                title=f["title"],
                description=f["description"],
                published_at=f["published_at"],
                create_at=f["created_at"],
                questions=[]
            )
            for q in f["questions"].values():
                question = FormQuestion(id=q["id"],question=q["question"],required=q["required"],type= q["type"],choices=q["choices"])
                form.questions.append(question)
            form_list.append(form)

        return form_list, count
