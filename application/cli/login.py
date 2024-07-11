import os
import requests
from application.cli.models import UserConf
import config
import json
import webbrowser



"""
File format should be

name=Example name
id=sdasdasdasd
email=emample@gmail.com
name=Tom Iss
token=2342342342sdfsdfsdfsdf
"""


def sanitize_value(value: str):
    return value.replace('"', "").strip()


def parse_conf_file(lines: list[str]) -> dict:
    conf = {}
    for line in lines:
        if "=" not in line or line.startswith("#"):
            continue

        [key, value] = line.split("=")
        conf[key.strip()] = sanitize_value(value)

    return conf


def check_login():
    path = config.config.get("config_file_path")
    if not os.path.exists(path):
        with open(path, "w"):
            ...

    lines = []
    with open(path, "r") as f:
        lines = f.readlines()

    parsed_conf = parse_conf_file(lines)

    if not bool(parsed_conf):
        return None
    user_id = parsed_conf.get("id")
    name = parsed_conf.get("name")
    email = parsed_conf.get("email")
    token = parsed_conf.get("token")

    if user_id is None or token is None or email is None:
        return None

    return UserConf(id=user_id, name=name, email=email, token=token)


def write_conf_to_file(id: str, name: str, email: str, session: str) -> bool:
    file_content = f"id={id}\nemail={email}\nname={name}\ntoken={session}\n"

    path = config.config.get("config_file_path")
    try:
        with open(path, "w") as f:
            f.write(file_content)
    except Exception:
        return False

    return True


def login():
    base_url = config.config.get("app_url")

    resp = requests.get(f"{config.config["app_url"]}/login-cli-verify/get-token")

    if resp.status_code != 200:
        print("Login failed")
    token_response = resp.json()
    token = token_response.get("token")
    url = f"{base_url}/login-cli-verify/?origin=cli&token={token}"
    webbrowser.open(url)
    print(f"Open browser to {url} and login")

    code = input("Input code: ")

    if len(code) != 6:
        raise Exception("You entered invalid code")

    data = json.dumps({"code": code, "token": token})

    resp = requests.post(
        f"{config.config["app_url"]}/login-cli-verify/verify", data=data
    )

    status = resp.status_code

    if status == 403 or status == 400:
        raise Exception(resp.json().get("detail") or "User login failed")

    if status != 200:
        return None

    response_data = resp.json()
    user = response_data.pop("user")
    token = response_data.get("token")

    user_id = user.get("id")
    name = user.get("name")
    email = user.get("email")

    is_logged_in = write_conf_to_file(id=user_id, email=email, name=name, session=token)

    if not is_logged_in:
        return None

    return UserConf(id=user_id, email=email, name=name, token=token)


def authenticate():
    user = check_login() or login()

    if user is None:
        print("Login failed, Ending program")
        quit(0)

    return user
