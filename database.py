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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                file_type TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

def saqla_kino(file_id: str, file_type: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kinolar (file_id, file_type) VALUES (?, ?)", (file_id, file_type))
    kino_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return kino_id

def olish_kino(kino_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, file_type FROM kinolar WHERE id = ?", (kino_id,))
    result = cursor.fetchone()
    conn.close()
    return result
