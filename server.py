from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from fastapi.staticfiles import StaticFiles
from app.http import router


app = FastAPI(
    debug=config.get("debug"),
    description=config.get("app_description"),
    title=config.get("app_name"),
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["http://localhost:8000"],
)

app.mount("/static", StaticFiles(directory="public/static"), name="static")
app.include_router(router=router)
