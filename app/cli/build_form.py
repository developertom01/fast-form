from lib.form import (
    FormBuilder,
    InvalidFilePathError,
    InvalidFileFormatError,
    SupportedFileTypeYAML,
    SupportedFileTypeJSON,
    SupportedFileTypeYML,
)
from config import config
import requests
import json
from app.http.form import CreateFormRequest

def build(path: str = "", session:str | None = None):
    print("Creating your form 👷🔧🪚")
    form_builder = FormBuilder()
    # Prompt user for file path and check if file path exists
    if path is None or path == "":
        try:
            path = form_builder.get_file_path()
        except InvalidFilePathError as e:
            print(e)
            return

    try:
        file_type = form_builder.get_file_type(path)
    except InvalidFileFormatError as e:
        print(e)
        return
    data = {}
    if file_type == SupportedFileTypeJSON:
        data = form_builder.read_json(path=path)
        # Read json
    elif file_type == SupportedFileTypeYAML or file_type == SupportedFileTypeYML:
        data = form_builder.read_yaml_file(path=path)
    
    # Validate input from questions uploaded

    questions_validation_error = form_builder.validate(data=dict(data))
    if len(questions_validation_error) != 0:
        print(questions_validation_error)
        return

    return upload_form(data, session)


def upload_form(form:dict, session:str):
    CreateFormRequest.model_validate_json(json.dumps(form))
    response = requests.post(f"{config.get("app_url")}/forms", data=json.dumps(form),cookies={"session": session})
    if response.status_code == 201:
        print("Form created suceefully ✅")
        data = response.json()
        published_key = data.get("published_key") 
        if data.get("published_at") is not None and published_key is not None:
            print(f"Form is published successfully ⚡️ \n\n You can access published form at {config["app_url"]}/forms/published/{published_key}")
    elif response.status_code == 400:
        print("Validation error: ", response.json())
    elif response.status_code == 401 or response.status_code == 403:
        raise Exception("NOT_LOGGED_IN")
    else:
        raise Exception("Unknown error 🫣")
        