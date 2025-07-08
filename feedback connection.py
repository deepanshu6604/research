import sqlite3
from config import SQLITE_DB_PATH

def init_feedback_db():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            feedback TEXT
        )
    """)
    conn.commit()
    conn.close()

def store_feedback(user_id, feedback_text):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (user_id, feedback) VALUES (?, ?)", (user_id, feedback_text))
    conn.commit()
    conn.close()

init_feedback_db()
