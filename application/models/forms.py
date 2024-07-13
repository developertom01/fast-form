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
        data:list[Form] = []
        count = 0

        for row in rows:
            count = row[0]
            data.append(Form(
                id=row[1],
                title=row[2],
                description= row[3],
                published_at= get_published_at_formatted(row[5]),
                created_at=humanize.naturaltime(datetime.fromisoformat(row[6]))
             ))

        return data, count

def get_published_at_formatted(published_at:str|None):
    return humanize.naturaltime(datetime.fromisoformat(published_at)) if  published_at is not None else "Not Published"