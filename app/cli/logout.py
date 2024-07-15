from config import config


def logout():
    path = config.get("config_file_path")
    with open(path, "w") as f:
        f.write("")
