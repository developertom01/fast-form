from fastapi import APIRouter, Request, Depends
from utils.templates import templates
from application.http.dependents import login_required
from fastapi.responses import RedirectResponse
import logging

index_route = APIRouter()


@index_route.get("/", name="index")
async def index(request: Request, user=Depends(login_required)):
    if user is None:
        logging.info("User not logged in, redirecting to /login")
        return RedirectResponse("/login/?origin=web", status_code=303)
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Dashboard",
        },
    )

    return response
