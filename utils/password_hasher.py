import bcrypt


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes(password, "utf-8"), salt)

    return hashed.decode("utf-8")


def compare_password(hashed: str, plain_password: str) -> bool:
    return bcrypt.checkpw(
        hashed_password=bytes(hashed, "utf-8"), password=bytes(plain_password, "utf-8")
    )
