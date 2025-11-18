import sqlite3
from contextlib import contextmanager

DB_NAME = 'cinema_bot.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            file_id TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()

def add_user(user_id, username):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()

def get_user_count():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

def add_movie(code, title, file_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (code, title, file_id) VALUES (?, ?, ?)", (code, title, file_id))
        conn.commit()

def get_movie_by_code(code):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_id, title FROM movies WHERE code = ?", (code,))
        return cursor.fetchone()
