from fastapi import APIRouter, Request, Form, Depends, Query, Response
from fastapi.responses import RedirectResponse
import nanoid
from utils.templates import templates
from utils.password_hasher import hash_password
from internal.database import get_db
from aiosqlite import Connection
import re
import logging

signup_router = APIRouter()


@signup_router.get("/", name="signup")
async def signup(
    request: Request,
    origin: str = Query("web"),
):
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={"title": "signup", "origin": origin},
    )


def validate_signup_form(email: str, password: str):
    error_occurred = False
    errors = {"email": [], "password": []}
    if not email:
        error_occurred = True
        errors["email"] = ["Email is required"]

    elif not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        error_occurred = True
        errors["email"] = ["Must be a valid email"]

    if not password:
        error_occurred = True
        errors["password"] = ["Password is required"]

    return errors, error_occurred


@signup_router.post("/", name="submit-form")
async def submit_form(
    request: Request,
    origin: str = Query("web"),
    email=Form(default=""),
    name=Form(default=""),
    password=Form(default=""),
    conn: Connection = Depends(get_db),
):
    errors, error_occurred = validate_signup_form(email=email, password=password)

    if error_occurred:
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={"title": "signup", "errors": errors, "origin": origin},
        )

    user_id = nanoid.generate()
    hashed_password = hash_password(password=password)
    try:
        await conn.execute(
            "INSERT INTO users (id,name,email, password) VALUES (?, ?, ?, ?)",
            (user_id, name, email, hashed_password),
        )
        await conn.commit()
    except Exception as e:
        logging.error(str(e), stack_info=True)
        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "title": "signup",
                "message": {"detail": "Server error", "type": "error"},
            },
        )

    return RedirectResponse(f"/login/?origin={origin}", status_code=303)
