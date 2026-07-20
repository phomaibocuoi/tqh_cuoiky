import sqlite3
from pathlib import Path
import json
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "logs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_prompt TEXT,
            ai_generated_code TEXT,
            final_edited_code TEXT,
            execution_status TEXT,
            execution_result TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_log(user_prompt: str, ai_code: str, final_code: str, status: str, result: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO api_logs (timestamp, user_prompt, ai_generated_code, final_edited_code, execution_status, execution_result) VALUES (?, ?, ?, ?, ?, ?)",
        (timestamp, user_prompt, ai_code, final_code, status, result)
    )
    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM api_logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Initialize db when this module is imported
init_db()
