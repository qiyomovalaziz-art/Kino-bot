# database.py
import sqlite3
import os

DB_PATH = "kinolar.db"

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE kinolar (
                kod TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                file_type TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

def saqla_kino(kod: str, file_id: str, file_type: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO kinolar (kod, file_id, file_type) VALUES (?, ?, ?)",
                   (kod, file_id, file_type))
    conn.commit()
    conn.close()

def olish_kino(kod: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, file_type FROM kinolar WHERE kod = ?", (kod,))
    result = cursor.fetchone()
    conn.close()
    return result  # (file_id, file_type) yoki None
