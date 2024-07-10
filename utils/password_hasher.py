import bcrypt

def hash_password(password:str)->str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)

    return hashed

def compare_password(hashed:str, plain_password:str)->bool:
    return bcrypt.checkpw(hashed_password=hashed,password=plain_password)