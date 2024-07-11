from fastapi import APIRouter, Request, Form, Depends, Query
from fastapi.responses import RedirectResponse
from datetime import datetime
from internal.cache import cache
import nanoid
from utils.templates import templates
from utils.password_hasher import compare_password
from internal.database import get_db
from aiosqlite import Connection
from application.dependents.login_required import login_required
from application.models import User
import re
import logging


TEMPLATE_FILE_NAME = "login.html"

login_router = APIRouter()


@login_router.get("/", name="login")
async def login(
    request: Request,
    origin: str = Query("web"),
    token: str = Query(""),
    user: User | None = Depends(login_required),
):
    if user is not None:
        return redirect_when_logged_in(user_id=user.id, origin=origin, token=token)

    return templates.TemplateResponse(
        request=request,
        name=TEMPLATE_FILE_NAME,
        context={"title": "Login", "origin": origin},
    )


def validate_login_form(email: str, password: str):
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


def redirect_when_logged_in(user_id, origin: str, token: str | None = None):
    url = "/"
    if origin == "cli":
        url = f"/login-cli-verify?origin=cli&token={token}"

    session_key = nanoid.generate(size=32)
    cache[f"session-{session_key}"] = {
        "user_id": user_id,
        "time": datetime.now().isoformat(),
    }

    response = RedirectResponse(url=url, status_code=303)
    response.set_cookie(key="session", value=session_key)

    return response


@login_router.post("/", name="submit-login-form", response_class=RedirectResponse)
async def submit_form(
    request: Request,
    origin: str = Query("web"),
    token: str = Query(""),
    email=Form(default=""),
    password=Form(default=""),
    conn: Connection = Depends(get_db),
):
    errors, error_occurred = validate_login_form(email=email, password=password)

    if error_occurred:
        return templates.TemplateResponse(
            request=request,
            name=TEMPLATE_FILE_NAME,
            context={"title": "Login", "errors": errors, "origin": origin},
        )

    user_row = None
    try:
        async with await conn.execute(
            "SELECT id, email, password FROM users WHERE email=? LIMIT 1", (email,)
        ) as cur:
            user_row = await cur.fetchone()
    except Exception as e:
        logging.error(str(e), stack_info=True)
        return templates.TemplateResponse(
            request=request,
            name=TEMPLATE_FILE_NAME,
            context={
                "title": "Login",
                "message": {"detail": "Server error", "type": "error"},
            },
        )

    if user_row is None:
        return templates.TemplateResponse(
            request=request,
            name=TEMPLATE_FILE_NAME,
            context={
                "title": "Login",
                "message": {"detail": "Login failed: User not found", "type": "error"},
            },
        )

    user_id, _, user_password = user_row
    if not compare_password(hashed=user_password, plain_password=password):
        return templates.TemplateResponse(
            request=request,
            name=TEMPLATE_FILE_NAME,
            context={
                "title": "Login",
                "message": {
                    "detail": "Login failed: Invalid password",
                    "type": "error",
                },
            },
        )

    return redirect_when_logged_in(user_id=user_id, origin=origin, token=token)
