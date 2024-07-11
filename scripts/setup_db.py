import sqlite3
import os


def read_sql():
    sqls = {}
    path = os.path.join(os.getcwd(), "scripts", "tables")
    for file in os.listdir(path=path):
        filename, ext = os.path.splitext(file)
        if ext != ".sql":
            continue
        file_path = os.path.join(path, file)

        with open(file=file_path, mode="r") as f:
            sql = f.read()
            sqls[filename] = sql

    return sqls


path = os.path.join(os.getcwd(), "db.sqlite")

try:
    with sqlite3.connect(path) as conn:
        sqls = read_sql()
        for table in sqls.keys():
            print(f"Running migration for {table}")
            conn.execute(sqls[table])
except Exception as e:
    print("Table migration failed", e)
