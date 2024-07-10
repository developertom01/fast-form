from dotenv import load_dotenv
import os

load_dotenv(".env")

config = {
    "app_name":"Fast Form",
    "app_env": os.environ.get("APP_ENV", "dev"),
    "debug": os.environ.get("APP_ENV", "dev") == "dev",
    "app_description":"A simple way to generate form for users",
    

}