import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "harmwatch.db")

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT, date TEXT, author_hash TEXT,
        url TEXT, domain TEXT,
        text TEXT, clean_text TEXT,
        category TEXT, risk_level TEXT
    )""")
    con.commit()
    con.close()

def insert_df(df: pd.DataFrame):
    con = sqlite3.connect(DB_PATH)
    df.to_sql("posts", con, if_exists="append", index=False)
    con.close()
