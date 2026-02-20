# ----- HEADER --------------------------------------------------

# File: log_service.py
# Description: Auto-generated header for structural compliance.

# ----- LIBRARY --------------------------------------------------

import json as L_JSON
import os as L_OS
from datetime import datetime as L_Date, timedelta as L_Delta
from typing import Any, Dict, Optional, Union, Literal
from backend.core import database as DB

# ----- VARIABLE --------------------------------------------------

# Legacy path (unused now)
LOG_FILE_PATH: str = "SQLite Database"
LogType = Literal["error", "alert", "transaction"]

# ----- FUNCTION --------------------------------------------------

import functools
import traceback

def F_Error_Handler(p_title: str):
    """
    Decorator to catch and log exceptions automatically.
    """
    def decorator(p_func):
        @functools.wraps(p_func)
        def wrapper(*args, **kwargs):
            try:
                return p_func(*args, **kwargs)
            except Exception as e:
                stack = traceback.format_exc()
                F_Add_Log('error', p_title, f"Exception in {p_func.__name__}: {str(e)}\n{stack}")
                return None
        return wrapper
    return decorator

def F_Add_Log_Path(p_path: str) -> str: return LOG_FILE_PATH
def F_Get_Log_Path() -> str: return LOG_FILE_PATH

# DESC: Reads the log file and returns its content as a dictionary.
# ADAPTED: Fetches logs for today to simulate old behavior for current day
def F_Get_Log_File() -> Dict[str, Dict[str, Dict[str, Dict[str, str]]]]:
    # This function returned ALL logs in a massive dictionary.
    # For SQLite, retrieving EVERYTHING is bad practice.
    # However, to maintain compatibility without breaking callers that expect the whole tree:
    # We will warn or return just today's logs?
    # Let's check usage. usages seem to call F_Get_Log(date) mostly.
    # But F_Add_Log calls this to append.
    # In SQL we don't need to read all to append.
    return {}

# DESC: Writes the given dictionary structure to the log file.
# DEPRECATED
def F_Add_Log_File(p_data: Dict[str, Any]) -> bool: return False

# DESC: Adds a new log entry.
def F_Add_Log(
    p_log_type: LogType, 
    p_title: str, 
    p_description: str,
    p_timestamp: Optional[L_Date] = None
) -> bool:
    # Input validation
    if p_log_type not in ["error", "alert", "transaction"]:
        print(f"Error: Invalid log type: {p_log_type}")
        return False
        
    if not p_title: # Allow non-string?
        print("Error: Log title is required")
        return False
        
    timestamp = p_timestamp if p_timestamp is not None else L_Date.now()
    timestamp_str = timestamp.isoformat()
    
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (type, title, description, timestamp) VALUES (?, ?, ?, ?)",
            (p_log_type, str(p_title), str(p_description), timestamp_str)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding log: {e}")
        return False

# DESC: Retrieves logs by date and optionally by log type.
def F_Get_Log(
    p_date: Optional[str] = None, 
    p_log_type: Optional[LogType] = None
) -> Dict[str, Any]:
    if p_date is None: p_date = L_Date.now().strftime('%Y-%m-%d')
    try: L_Date.strptime(p_date, '%Y-%m-%d')
    except ValueError:
        print(f"Error: Invalid date format. Expected 'YYYY-MM-DD', got: {p_date}")
        return {}
    
    conn = DB.get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM logs WHERE timestamp LIKE ?"
    params = [f"{p_date}%"]
    
    if p_log_type:
        query += " AND type = ?"
        params.append(p_log_type)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Reconstruct dictionary structure: Type -> Time -> Data
    # Existing format: { "error": { "12:00:00": { ... } } }
    
    result = {}
    if p_log_type:
        result = {} # If specific type requested, return just that dict (Time -> Data)?
        # Check original: if p_log_type is set, returns date_logs.get(p_log_type, {})
        # So it returns { "time": data }
        for row in rows:
            dt = L_Date.fromisoformat(row['timestamp'])
            time_str = dt.strftime('%H:%M:%S')
            result[time_str] = {
                "title": row['title'],
                "description": row['description'],
                "timestamp": row['timestamp']
            }
        return result
    else:
        # Return { "type": { "time": data } }
        result = {"error": {}, "alert": {}, "transaction": {}}
        for row in rows:
            l_type = row['type']
            if l_type not in result: result[l_type] = {}
            
            dt = L_Date.fromisoformat(row['timestamp'])
            time_str = dt.strftime('%H:%M:%S')
            
            result[l_type][time_str] = {
                "title": row['title'],
                "description": row['description'],
                "timestamp": row['timestamp']
            }
        return result

# DESC: Deletes a specific log entry.
def F_Del_Log(p_date: str, p_log_type: LogType, p_time: str) -> bool:
    # Need to match timestamp loosely? ISO format contains milliseconds sometimes.
    # Searching by combined date+time string
    try:
        timestamp_pattern = f"{p_date}T{p_time}%" # ISO separator is T
        
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM logs WHERE type = ? AND timestamp LIKE ?",
            (p_log_type, timestamp_pattern)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception as e:
        print(f"Error deleting log: {e}")
        return False

# DESC: Deletes all logs older than the specified number of days.
def F_Del_Historical_Log(p_days_ago: int) -> bool:
    if not isinstance(p_days_ago, int) or p_days_ago < 0: return False
    if p_days_ago == 0: return True
    
    try:
        cutoff_date = L_Date.now() - L_Delta(days=p_days_ago)
        cutoff_str = cutoff_date.isoformat()
        
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs WHERE timestamp < ?", (cutoff_str,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting historical logs: {e}")
        return False
