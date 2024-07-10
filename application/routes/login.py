from fastapi import APIRouter, Request, Form, Depends, Query, Response
from fastapi.responses import RedirectResponse
from datetime import datetime
from internal.cache import cache
import uuid
import nanoid
from utils.templates import templates
from utils.password_hasher import compare_password
from internal.database import get_db
from aiosqlite import Connection
import re
import logging

login_router= APIRouter()

@login_router.get("/",name="login")
async def login(request: Request, origin:str =Query("web"),):
    return templates.TemplateResponse(
        request= request,
        name="login.html",
        context={
            "title": "Login",
            "origin": origin
        }
    )

def validate_login_form(email: str, password:str):
    error_occurred=False
    errors = {
        "email": [],
        "password": []
    }
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

@login_router.post("/",name="submit-login-form", response_class=RedirectResponse)
async def submit_form(request:Request, origin:str =Query("web"), email= Form(default=""), password= Form(default=""), conn:Connection =  Depends(get_db)):
    errors, error_occurred = validate_login_form(email=email, password= password)

    if error_occurred:
        return templates.TemplateResponse(
        request= request,
        name="login.html",
        context={
            "title": "Login",
            "errors": errors,
            "origin": origin
        }
    )

    user_row = None
    try:
        async with await conn.execute("SELECT id, email, password FROM users WHERE email=? LIMIT 1",(email, )) as cur:
            user_row =await cur.fetchone()
    except Exception as e:
        logging.error(str(e), stack_info=True)
        return templates.TemplateResponse(
        request= request,
        name="login.html",
        context={
            "title": "Login",
            "message":  {
               "detail": "Server error",
               "type": "error"
            }
        }
    )

    if user_row is None:
        return templates.TemplateResponse(
        request= request,
        name="login.html",
        context={
            "title": "Login",
            "message": {
               "detail": "Login failed: User not found",
               "type": "error"
            }
        }
    )

    user_id, _ , user_password = user_row
    if not compare_password(hashed= user_password, plain_password= password):
        return templates.TemplateResponse(
        request= request,
        name="login.html",
        context={
            "title": "Login",
            "message": {
               "detail": "Login failed: Invalid password",
               "type": "error"
            }
        }
    )

    if origin == "cli":
        code = nanoid.generate(size=6)
        cache[code] = { 
            "user_id":user_id, 
            "time": datetime.now().isoformat() 
        }
        return RedirectResponse(f"/login-cli-verify/?code={code}", status_code=303)
    
    session_value = nanoid.generate(size=32)
    cache[session_value] = {
        "user_id": user_id,
        "time": datetime.now().isoformat() 
    }
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="session",
        value= session_value
        )
    return response