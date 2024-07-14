from fastapi import APIRouter, Request, Depends, Query
from utils.templates import templates
from application.http.dependents import login_required, FetchPaginatedForm
from fastapi.responses import RedirectResponse
import logging
from urllib import parse

logger = logging.getLogger(__name__)

index_route = APIRouter()


@index_route.get("/", name="index")
async def index(
    request: Request,
    user=Depends(login_required),
    page: int | None = Query(default=1),
    size: int | None = Query(default=12),
    forms_service: FetchPaginatedForm = Depends(FetchPaginatedForm),
):
    if user is None:
        logging.info("User not logged in, redirecting to /login")
        return RedirectResponse(f"/login/?origin={parse.quote("web")}&redirect={parse.quote(f"/?page={page}&size={size}")}", status_code=303)
    form_resource = None
    try:
        form_resource = await forms_service.fetch(user=user)

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": "Dashboard",
                "forms": form_resource.model_dump(),
                "user": dict(user),
            },
        )
    except Exception as e:
        logger.error(e)
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": "Dashboard",
                "message": {
                    "type": "error",
                    "detail": "An error occured while fetching forms. Reload page to retry",
                },
            },
        )
