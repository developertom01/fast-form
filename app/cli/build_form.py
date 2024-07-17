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
from app.models import PaginationResource, Form

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

def publish_form(form_id:str, session:str):
    response = requests.patch(f"{config.get("app_url")}/forms/api/{form_id}/publish", data=json.dumps({}),cookies={"session": session})
    if response.status_code == 200:
        print("You have successfully published form  ✅")
    elif response.status_code == 400:
        print("Validation error: ", response.json())
    elif response.status_code == 401 or response.status_code == 403:
        raise Exception("NOT_LOGGED_IN")
    elif response.status_code == 404:
        raise Exception("Form not found")
    else:
        raise Exception("Unknown error 🫣")    
    
def unpublish_form(form_id:str, session:str):
    response = requests.patch(f"{config.get("app_url")}/forms/api/{form_id}/unpublish", data=json.dumps({}),cookies={"session": session})
    if response.status_code == 200:
        print("You have successfully unpublished form ✅")
    elif response.status_code == 400:
        print("Validation error: ", response.json())
    elif response.status_code == 401 or response.status_code == 403:
        raise Exception("NOT_LOGGED_IN")
    elif response.status_code == 404:
        raise Exception("Form not found")
    else:
        raise Exception("Unknown error 🫣") 

def delete_form(form_id:str, session:str):
    response = requests.delete(f"{config.get("app_url")}/forms/api/{form_id}/delete",cookies={"session": session})
    if response.status_code == 202:
        print("Form created delete form ✅")
    elif response.status_code == 400:
        print("Validation error: ", response.json())
    elif response.status_code == 401 or response.status_code == 403:
        raise Exception("NOT_LOGGED_IN")
    elif response.status_code == 404:
        raise Exception("Form not found")
    else:
        raise Exception("Unknown error 🫣")
      
def list_forms(session:str, page:int, per_page:int):
    response = requests.get(f"{config.get("app_url")}/forms/?page={page}&size={per_page}",cookies={"session": session})
    if response.status_code == 200:
        return PaginationResource[Form].model_validate(response.json())
    elif response.status_code == 400:
        print("Validation error: ", response.json())
    elif response.status_code == 401 or response.status_code == 403:
        raise Exception("NOT_LOGGED_IN")
    else:
        raise Exception("Unknown error 🫣")

def print_forms(forms:list[Form], page:int = 1):
    print("********** LIST OF FORMS **********\n")
    for i, form in enumerate(forms):
        print(f"{page*(i+1)} id: {form.id}\t title:{form.title} \t \n\n")
        print("-"*50, "\n")
    print("********** END OF LIST **********\n")


def perform_list_forms_itr(session:str, page=1):
    print("Fetching set of forms ...")
    per_page = 5
    paginated_form = list_forms(session=session,per_page=per_page,page=page)
    print_forms(paginated_form.data, page=page)
    while paginated_form.page < paginated_form.last:
        action = input("Press (YES/Y) to fetch more or different key to quite: ").lower()
        if action == "y" or action == "yes":
            perform_list_forms_itr(session=session,page=paginated_form.next)
        else: 
            break
    print("Ended fetch")
    quit(0)
     

