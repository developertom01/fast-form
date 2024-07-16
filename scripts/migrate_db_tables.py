import sqlite3
import os


def read_sql():
    sqls = []
    tables = []
    path = os.path.join(os.getcwd(), "scripts", "tables")
    for file in os.listdir(path=path):
        filename, ext = os.path.splitext(file)
        if ext != ".sql":
            continue
        file_path = os.path.join(path, file)

        with open(file=file_path, mode="r") as f:
            sql = f.read()
            sqls.append(sql)
            tables.append(filename)
    # Reverse order to run migration from top to bottom. Order is important
    return sqls, tables


path = os.path.join(os.getcwd(), "db.sqlite")
sqls, tables = read_sql()

try:
    with sqlite3.connect(path) as conn:
        for i, sql in enumerate(sqls):
            print(f"Running migration for {tables[i]}")
            conn.execute(sql)
            conn.commit()
except Exception as e:
    print("Table migration failed", e)
