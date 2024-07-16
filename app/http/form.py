from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import RedirectResponse
from datetime import datetime
from lib.form import FormBuilder
from pydantic import BaseModel, Field, ValidationError
from enum import Enum
from app.models import User, Form, PaginationResource
from aiosqlite import Connection
from internal.database import get_db
from nanoid import generate
from app.http.dependents import (
    login_required,
    FetchPaginatedForm,
)
from app.exceptions import UserNotLoggedInException, ValidationException, NotFoundError
import logging
import json
from utils.templates import templates
from urllib import parse


logger = logging.getLogger(__name__)

form_route = APIRouter()


class DataTypeEnum(str, Enum):
    text = "text"
    number = "number"
    boolean = "boolean"
    choice = "choice"


class FormQuestionRequestPayload(BaseModel):
    question: str
    type: DataTypeEnum
    required: bool
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
    forms: CreateFormRequest,
    user: User | None = Depends(login_required),
    db_conn: Connection = Depends(get_db),
):
    try:
        if user is None:
            raise UserNotLoggedInException("User not logged in")

        # Validate
        form_builder = FormBuilder()
        errors = form_builder.validate(forms.model_dump())
        if len(errors) != 0:
            raise ValidationException(errors)
        # Will be inserting in multiple tables so begin transaction
        form_row = None
        async with db_conn.execute("begin;") as cur:
            form_id = generate(size=32)
            now = datetime.now().isoformat()
            published_at = get_published_at(forms.publish)
            published_key = None
            if forms.publish:
                published_key = generate(size=32)
            await cur.execute(
                """
                    INSERT INTO forms (id, title, description, user_id, published_at, created_at,published_key)
                    VALUES(?,?,?,?,?,?,?)
                    RETURNING id, title,description,published_at,created_at,published_key
                """,
                (
                    form_id,
                    forms.title,
                    forms.description,
                    user.id,
                    published_at,
                    now,
                    published_key,
                ),
            )
            form_row = await cur.fetchone()
            questions = [
                (generate(size=32), q.question, q.type.name, q.required, form_id)
                for q in forms.questions
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
                    c,
                    questions[i][0],
                )
                for i, q in enumerate(forms.questions)
                if q.type == DataTypeEnum.choice and q.choices is not None
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
        form = Form(
            id=form_row[0],
            title=form_row[1],
            description=form_row[2],
            published_at=form_row[3],
            created_at=form_row[4],
            published_key = form_row[5]
        )
        return Response(content=form.model_dump_json(), status_code=201)

    except Exception as e:
        logger.error(e)
        status = 500
        error = "Server error"

        if isinstance(e, UserNotLoggedInException):
            status = 401
            error = "UnAuthorized"

        elif isinstance(e, ValidationException):
            error = e.errors
            status = 400
        elif isinstance(e, ValidationError):
            error = e.json()
            status = 400
        return Response(json.dumps({"detail": error}), status_code=status)


@form_route.get("/", response_model=PaginationResource[Form])
async def get_user_forms(
    user: User | None = Depends(login_required),
    fetch_form_service: FetchPaginatedForm = Depends(FetchPaginatedForm),
):

    try:
        if user is None:
            raise UserNotLoggedInException("User not logged in")

        resource = await fetch_form_service.fetch(user=user)

        return resource

    except Exception as e:
        logger.error(str(e))
        status = 500
        error = "Server error"

        if isinstance(e, UserNotLoggedInException):
            status = 401
            error = "UnAuthorized"

        return Response(json.dumps({"detail": error}), status_code=status)


@form_route.get("/{form_id}")
async def get_form(
    request: Request,
    form_id: str,
    user=Depends(login_required),
    forms_service: FetchPaginatedForm = Depends(FetchPaginatedForm),
):
    if user is None:
        logging.info("User not logged in, redirecting to /login")
        return RedirectResponse(
            f"/login/?origin=web&redirect={parse.quote(f"/forms/{form_id}")}",
            status_code=303,
        )
    try:
        form = await forms_service.fetch_questions(form_id=form_id)
        return templates.TemplateResponse(
            request=request,
            name="form-detail.html",
            context={"form": form},
        )
    except Exception as e:
        logger.error(e)
        error = "Server error"
        if isinstance(e, NotFoundError):
            error = str(e)

        return templates.TemplateResponse(
            request=request,
            name="form-detail.html",
            context={"message": {"type": "error", "detail": error}},
        )
