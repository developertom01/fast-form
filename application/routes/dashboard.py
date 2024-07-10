from fastapi import APIRouter, Request, Response
from utils.templates import templates


index_route= APIRouter()

@index_route.get("/", name="index")
async def login(request: Request, response: Response):    
    response= templates.TemplateResponse(
        request= request,
        name="index.html",
        context={
            "title": "Dashboard",
        }
    )
    
    return response