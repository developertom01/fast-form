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

@form_route.patch("/api/{form_id}/publish")
async def api_publish_form(
    form_id: str,
    user=Depends(login_required),
    forms_service: FetchPaginatedForm = Depends(FetchPaginatedForm),
):
    try:
        if user is None:
            logging.info("User not logged in")
            raise UserNotLoggedInException("")
        
        published_key=generate(size=32)
        await forms_service.publish_form(form_id=form_id,published_key=published_key, user_id=user.id)
        return {"status":"ok"}
    except Exception as e:
        logger.error(e)
        error = "Internal server error"
        status = 500
        if isinstance(e, NotFoundError):
            error = str(e)
            status = 404
        if isinstance(e, UserNotLoggedInException):
            error = "Unauthorized"
            status = 401

        return Response(content=json.dumps({"detail": error}),status_code=status)
    
@form_route.delete("/api/{form_id}/delete")
async def api_publish_form(
    form_id: str,
    user=Depends(login_required),
    forms_service: FetchPaginatedForm = Depends(FetchPaginatedForm),
):
    try:
        if user is None:
            logging.info("User not logged in")
            raise UserNotLoggedInException("")
        
        await forms_service.delete_form(form_id=form_id, user_id=user.id)
        return Response(status_code=202)
    except Exception as e:
        logger.error(e)
        error = "Internal server error"
        status = 500
        if isinstance(e, NotFoundError):
            error = str(e)
            status = 404
        if isinstance(e, UserNotLoggedInException):
            error = "Unauthorized"
            status = 401
        else:
            raise e

        return Response(content=json.dumps({"detail": error}),status_code=status)
    
@form_route.patch("/api/{form_id}/unpublish")
async def api_unpublish_form(
    form_id: str,
    user=Depends(login_required),
    forms_service: FetchPaginatedForm = Depends(FetchPaginatedForm),
):
    try:
        if user is None:
            logging.info("User not logged in")
            raise UserNotLoggedInException("")
        
        await forms_service.unpublish_form(form_id=form_id, user_id=user.id)
        return {"status":"ok"}
    except Exception as e:
        logger.error(e)
        error = "Internal server error"
        status = 500
        if isinstance(e, NotFoundError):
            error = str(e)
            status = 404
        if isinstance(e, UserNotLoggedInException):
            error = "Unauthorized"
            status = 401

        return Response(content=json.dumps({"detail": error}),status_code=status)
       

@form_route.get("/{form_id}/publish")
async def publish_form(
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
        published_key=generate(size=32)
        await forms_service.publish_form(form_id=form_id,published_key=published_key, user_id=user.id)
        return  RedirectResponse(f"/forms/published/{published_key}",status_code=303)
    
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
    

@form_route.get("/{form_id}/unpublish")
async def unpublish_form(
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
        await forms_service.unpublish_form(form_id=form_id, user_id=user.id)
        return RedirectResponse(f"/forms/{form_id}",status_code=303)
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

@form_route.get("/{form_id}/delete")
async def delete_form(
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
        await forms_service.delete_form(form_id=form_id, user_id=user.id)
        return RedirectResponse("/",status_code=303)
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

@form_route.get("/published/{published_key}")
async def get_form(
    request: Request,
    published_key: str,
    forms_service: FetchPaginatedForm = Depends(FetchPaginatedForm),
):
    print(published_key)
    try:
        form = await forms_service.fetch_questions(form_id=None, published_key=published_key)
        return templates.TemplateResponse(
            request=request,
            name="published-form-view.html",
            context={"form": form},
        )
    except Exception as e:
        logger.error(e)
        error = "Server error"
        if isinstance(e, NotFoundError):
            error = str(e)

        return templates.TemplateResponse(
            request=request,
            name="published-form-view.html",
            context={"message": {"type": "error", "detail": error}},
        )

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
        form = await forms_service.fetch_questions(form_id=form_id,published_key=None, user_id=user.id)
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


