import aiosqlite
import os

db_path = os.path.join(os.getcwd(),"db.sqlite")

async def get_db(path = db_path):
    conn = await aiosqlite.connect(path)
    try:
        yield conn
    finally:
        await conn.close()
