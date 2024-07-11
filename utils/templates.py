from fastapi.templating import Jinja2Templates
import os

template_path = os.path.join(".", "templates")

templates = Jinja2Templates(directory=template_path)
