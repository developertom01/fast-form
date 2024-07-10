from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from datetime import datetime
import nanoid
import logging
from application.dependents.login_required import login_required
from internal.cache import cache
from utils.templates import templates

verify_route= APIRouter()

TEMPLATE_FILE_NAME = "login-cli-verify.html"

@verify_route.get("/")
def verify(request:Request, user = Depends(login_required)):
    if user is None:
        logging.info("User not logged in, redirecting to /login")
        return RedirectResponse("/login/?origin=cli",status_code=303)

    code = nanoid.generate(size=6,alphabet="1234567890ABCXYZ").upper()

    cache[code] = {
        "user_id": user.id,
        "time": datetime.now().isoformat()
    }


    return templates.TemplateResponse(
        request= request,
        name=TEMPLATE_FILE_NAME,
        context={
            "title": "Login",
            "code": code
        }
    )
