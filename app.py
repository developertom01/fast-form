from fastapi import FastAPI
from config import config
from fastapi.staticfiles import StaticFiles
from application.routes import router


app = FastAPI(
    debug = config.get("debug"),
    description = config.get("app_description"),
    title = config.get("app_name"),
    
)

app.mount("/static", StaticFiles(directory="public/static"), name="static")
app.include_router(router=router)
