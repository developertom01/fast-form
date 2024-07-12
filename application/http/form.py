from fastapi import APIRouter, Depends, Response
from datetime import datetime
from lib.form import FormBuilder
from pydantic import BaseModel, Field
from enum import Enum
from application.models import User
from aiosqlite import Connection
from internal.database import get_db
from nanoid import generate
from application.http.dependents import login_required
from application.exceptions import UserNotLoggedInException, ValidationException
import logging
import json

logger = logging.getLogger(__name__)

form_route = APIRouter()


class DataTypeEnum(Enum):
    text = "text"
    number = "number"
    boolean = "boolean"
    choice = "choice"


class FormQuestionRequestPayload(BaseModel):
    question: str
    type: DataTypeEnum
    is_required: bool
    choices: list[str] | None = Field(default=None, min_length=1, max_length=10)


class CreateFormRequest(BaseModel):
    title: str
    description: str | None = Field(default=None)
    publish: bool
    questions: list[FormQuestionRequestPayload] = Field(min_length=1, max_length=15)

    def __str__(self) -> str:
        return self.title


def get_published_at(published: bool):
    return datetime.now().isoformat() if published else None


@form_route.post("/", name="create_form")
async def create_form(
    payload: CreateFormRequest,
    user: User | None = Depends(login_required),
    db_conn: Connection = Depends(get_db),
):
    try:
        if user is None:
            raise UserNotLoggedInException("User not logged in")

        # Validate
        form_builder = FormBuilder()
        errors = form_builder.validate(payload.model_dump())
        if len(errors) != 0:
            raise ValidationException(errors)
        # Will be inserting in multiple tables so begin transaction
        async with db_conn.execute("begin") as cur:
            form_id = generate(size=32)
            now = datetime.now().isoformat()
            published_at = get_published_at(payload.publish)
            await cur.execute(
                """
                    INSERT INTO forms (id, title, description, user_id, published_at, created_at)
                    VALUES(?,?,?,?,?,?)
                """,
                (
                    form_id,
                    payload.title,
                    payload.description,
                    user.id,
                    published_at,
                    now,
                ),
            )
            questions = [
                (generate(size=32), q.question, q.type, q.is_required, form_id)
                for q in payload.questions
            ]
            await cur.executemany(
                """
                    INSERT INTO form_questions (id,question,type,is_required,form_id)
                    VALUES(?,?,?,?,?)
                """,
                questions,
            )

            question_choices = [
                (
                    generate(size=32),
                    questions[i][0],
                    c,
                )
                for i, q in enumerate(payload.questions)
                if q.type == "choices" and q.choices is not None
                for c in q.choices
            ]

            if len(question_choices) > 0:
                await cur.executemany(
                    """
                        INSERT INTO form_question_choices (id, choice, question_id)
                        VALUES (?, ?, ?)
                    """,
                    question_choices,
                )
            await cur.execute("commit;")

        return Response(status_code=201)

    except Exception as e:
        logger.error(str(e))
        status = 500
        error = "Server error"

        if isinstance(e, UserNotLoggedInException):
            status = 401
            error = "UnAuthorized"
            
        elif isinstance(e, ValidationException):
            error = e.errors
            status = 400
            
        return Response(json.dumps({"detail": error}), status_code=status)
