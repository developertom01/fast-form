from dotenv import load_dotenv
import os
load_dotenv(".env")

APP_STORAGE_FILE_NAME = ".fast_form"
user_path = os.path.expanduser("~")

config = {
    "app_name": "Fast Form",
    "app_env": os.environ.get("APP_ENV", "dev"),
    "debug": os.environ.get("APP_ENV", "dev") == "dev",
    "app_description": "A simple way to generate form for users",
    "app_url": os.environ.get("APP_URL", "http://127.0.0.1:8000"),
    "config_file_path": os.path.join(user_path, APP_STORAGE_FILE_NAME),
}