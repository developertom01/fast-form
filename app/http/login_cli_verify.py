from fastapi import APIRouter, Depends, Request, Query, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from app.models import CliLogin
from datetime import datetime
import nanoid
import logging
from app.http.dependents import login_required
from internal.cache import cache
from utils.templates import templates
import json
from urllib import parse

verify_route = APIRouter()

TEMPLATE_FILE_NAME = "login-cli-verify.html"


@verify_route.get("/")
def show_code(request: Request, user=Depends(login_required), token=Query(default="")):
    code = cache.get(token)
    message = None
    if code is None:
        message = {"type": "error", "detail": "Token not found"}

    if user is None:
        logging.info("User not logged in, redirecting to /login")
        return RedirectResponse(f"/login/?redirect={parse.quote(f"/login-cli-verify/?origin=cli&token={token}")}", status_code=303)

    cache[f"{code}.{token}"] = user
    return templates.TemplateResponse(
        request=request,
        name=TEMPLATE_FILE_NAME,
        context={"title": "Verify", "code": code, "message": message},
    )


@verify_route.get("/get-token", status_code=200)
async def get_token():
    token = nanoid.generate(size=32)
    code = nanoid.generate(size=6, alphabet="1234567890ABCXYZ").upper()
    cache[token] = code

    return {"token": token}


class VerifyTokenRequest(BaseModel):
    token: str | None = None
    code: str | None = None


@verify_route.post("/verify", status_code=200)
async def verify_code(payload: VerifyTokenRequest):
    status = 200
    error = ""
    is_error = False
    if not payload.token or not payload.code:
        is_error = True
        error = "token and code is required"
        status = 400

    stored_code = cache.get(payload.token)
    if not payload.code or payload.code != stored_code:
        is_error = True
        error = "Invalid code"
        status = 403

    user = cache.get(f"{payload.code}.{payload.token}")
    if user is None:
        is_error = True
        error = "Session expired"
        status = 403

    if is_error:
        return Response(json.dumps({"detail": error}), status_code=status)

    session_key = nanoid.generate(size=32)

    cache[f"session-{session_key}"] = {
        "user_id": user.id,
        "time": datetime.now().isoformat(),
    }
    response_body = CliLogin(user=user, token=session_key)
    response = Response(response_body.model_dump_json(), status_code=200)
    response.set_cookie(key="session", value=session_key, httponly=True)
    return response
