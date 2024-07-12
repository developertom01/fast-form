from fastapi import APIRouter, Depends, Response, Query
from datetime import datetime
from lib.form import FormBuilder
from pydantic import BaseModel, Field
from enum import Enum
from application.models import User
from aiosqlite import Connection
from internal.database import get_db
from nanoid import generate
from application.http.dependents import (
    login_required,
    get_pagination_parameters,
    PaginationParameters,
)
from application.exceptions import UserNotLoggedInException, ValidationException
import logging
import json
from utils.templates import templates

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


@form_route.get("/")
async def get_user_forms(
    user: User | None = Depends(login_required),
    db_conn: Connection = Depends(get_db),
    pagination_params:PaginationParameters = Depends(get_pagination_parameters)
):

    try:
        if user is None:
            raise UserNotLoggedInException("User not logged in")

        forms_itr = []
        async with db_conn.execute(
            """
            WITH total_count AS (
            SELECT COUNT(DISTINCT id) as total FROM forms
            WHERE forms.user_id=?
            )

            WITH paginated_data AS (
                 forms.id AS id
                forms.title AS title
                forms.description AS description
                forms.user_id AS user_id
                forms.published_at AS published_at
                forms.created_at AS created_at

                fq.id AS question_id
                fq.question AS question_question
                fq.type AS question_type
                fq.is_required AS question_is_required
                fq.form_at AS question_form_id

                fqc.id AS question_choice_id
                fqc.choice AS question_choice_choice
                fqc.question_id AS choice_question_id

                SELECT  FROM forms 
                LEFT JOIN form_questions AS fq ON forms.id=fq.form_id
                LEFT JOIN form_question_choices AS fqc ON fq.id=fqc.question_id

                WHERE forms.user_id=?
                LIMIT=?
                OFFSET=?
            )

            SELECT total_count.total AS count, paginated_data.*
            """,
            (user.id, pagination_params.limit, pagination_params.offset),
        ) as cur:
            forms_itr = await cur.fetchmany()

    except Exception as e:
        logger.error(str(e))
        status = 500
        error = "Server error"

        if isinstance(e, UserNotLoggedInException):
            status = 401
            error = "UnAuthorized"

        return Response(json.dumps({"detail": error}), status_code=status)
