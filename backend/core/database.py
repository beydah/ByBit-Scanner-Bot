# ----- HEADER --------------------------------------------------

# File: database.py
# Description: Auto-generated header for structural compliance.

import sqlite3
import json
import os
from typing import Any, Dict, List, Optional, Union
from threading import Lock

# Database Logic
DB_NAME = "bot_data.db"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", DB_NAME)
_db_lock = Lock()

def get_connection():
    """Returns a thread-safe connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with necessary tables."""
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Settings Table (Key-Value generic storage for app settings)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Periods Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS periods (
                name TEXT PRIMARY KEY,
                seconds INTEGER
            )
        ''')

        # Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                title TEXT,
                description TEXT,
                timestamp TEXT
            )
        ''')

        # Telegram Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                user_name TEXT,
                user_type BOOLEAN,
                user_active BOOLEAN,
                user_add_date TEXT
            )
        ''')

        # Messages Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Buttons Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buttons (
                menu_name TEXT,
                button_text TEXT,
                command TEXT,
                PRIMARY KEY (menu_name, button_text)
            )
        ''')
        
        conn.commit()
        conn.close()

# Helper functions for common operations

def kv_get(table: str, key: str, default: Any = None) -> Any:
    """Get a value from a key-value table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT value FROM {table} WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row[0])
        except:
            return row[0]
    return default

def kv_set(table: str, key: str, value: Any):
    """Set a value in a key-value table."""
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        val_str = json.dumps(value, ensure_ascii=False)
        cursor.execute(f"INSERT OR REPLACE INTO {table} (key, value) VALUES (?, ?)", (key, val_str))
        conn.commit()
        conn.close()

def kv_get_all(table: str) -> Dict[str, Any]:
    """Get all key-values from a table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT key, value FROM {table}")
    rows = cursor.fetchall()
    conn.close()
    result = {}
    for row in rows:
        try:
            result[row['key']] = json.loads(row['value'])
        except:
            result[row['key']] = row['value']
    return result

# Initialize DB on module import
init_db()
