from fastapi import Cookie, Depends
from typing import Annotated
import logging
from internal.cache import cache
from internal.database import get_db
from aiosqlite import Connection
from application.models.user import User
class NotLoginException(Exception):
    pass

async def login_required(session: Annotated[str | None, Cookie()] = None, conn: Connection = Depends(get_db)):
    try:
        if not session:
            raise NotLoginException("Authentication required")
    
        session_info:dict | None = cache.get(session)

        if session_info is None:
            raise NotLoginException("Authentication required")
        
        user_row = None
        async with conn.execute("SELECT id, name, email FROM users WHERE id=?",(session_info.get("user_id"), )) as cur:
            user_row = await cur.fetchone()
        
            user = User(id=user_row[0], name=user_row[1],email=user_row[2])
            return user
    except Exception as e:
        logging.error(e)
        return None
        