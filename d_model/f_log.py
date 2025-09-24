# ----- LIBRARY --------------------------------------------------

import json as L_JSON
import os as L_OS
from datetime import datetime as L_Date, timedelta as L_Delta
from typing import Any, Dict, Optional, Union, Literal

# ----- VARIABLE --------------------------------------------------

LOG_FILE_PATH: str = L_OS.path.join(L_OS.path.dirname(__file__), '..', 'e_database', 'f_log.json')
LogType = Literal["error", "alert", "transaction"]

# ----- FUNCTION --------------------------------------------------

# DESC: Sets the log file path and returns the new path.
def F_Add_Log_Path(p_path: str) -> str:
    if not isinstance(p_path, str) or not p_path.strip(): raise ValueError("Log file path must be a non-empty string")
    global LOG_FILE_PATH
    LOG_FILE_PATH = p_path.strip()
    return LOG_FILE_PATH

# DESC: Returns the path of the currently set log file.
def F_Get_Log_Path() -> str: return LOG_FILE_PATH

# DESC: Reads the log file and returns its content as a dictionary.
def F_Get_Log_File() -> Dict[str, Dict[str, Dict[str, Dict[str, str]]]]:
    if not L_OS.path.exists(LOG_FILE_PATH): return {}
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as file_handle:
            log_data = L_JSON.load(file_handle)
            if not isinstance(log_data, dict): return {}
            return log_data
    except (FileNotFoundError, L_JSON.JSONDecodeError) as e:
        print(f"Warning: Could not read log file: {e}")
        return {}

# DESC: Writes the given dictionary structure to the log file.
def F_Add_Log_File(p_data: Dict[str, Any]) -> bool:
    try:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        temp_path = f"{LOG_FILE_PATH}.tmp"
        with open(temp_path, 'w', encoding='utf-8') as file_handle: 
            L_JSON.dump(p_data, file_handle, indent=2, ensure_ascii=False)
            
        if os.path.exists(LOG_FILE_PATH): os.remove(LOG_FILE_PATH)
        os.rename(temp_path, LOG_FILE_PATH)
        return True
    except (IOError, OSError, TypeError) as e:
        print(f"Error writing to log file: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try: os.remove(temp_path)
            except OSError: pass
        return False

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
        
    if not p_title or not isinstance(p_title, str):
        print("Error: Log title is required and must be a string")
        return False
        
    timestamp = p_timestamp if p_timestamp is not None else L_Date.now()
    current_date = timestamp.strftime('%Y-%m-%d')
    current_time = timestamp.strftime('%H:%M:%S')
    all_logs = F_Get_Log_File()
    if current_date not in all_logs: all_logs[current_date] = {"error": {}, "alert": {}, "transaction": {}}
    all_logs[current_date][p_log_type][current_time] = {
        "title": p_title,
        "description": p_description,
        "timestamp": timestamp.isoformat()
    }
    return F_Add_Log_File(all_logs)

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
    
    all_logs = F_Get_Log_File()
    date_logs = all_logs.get(p_date, {})
    if p_log_type is not None:
        if p_log_type not in ["error", "alert", "transaction"]:
            print(f"Error: Invalid log type: {p_log_type}")
            return {}
        return date_logs.get(p_log_type, {})
    return date_logs

# DESC: Deletes a specific log entry.
def F_Del_Log(p_date: str, p_log_type: LogType, p_time: str) -> bool:
    if not all([p_date, p_log_type, p_time]):
        print("Error: All parameters must be non-empty")
        return False
        
    if p_log_type not in ["error", "alert", "transaction"]:
        print(f"Error: Invalid log type: {p_log_type}")
        return False
        
    try:
        L_Date.strptime(p_date, '%Y-%m-%d')
        L_Date.strptime(p_time, '%H:%M:%S')
    except ValueError as e:
        print(f"Error: Invalid date or time format: {e}")
        return False
    
    all_logs = F_Get_Log_File()
    if (p_date in all_logs and 
        p_log_type in all_logs[p_date] and 
        p_time in all_logs[p_date][p_log_type]):
        del all_logs[p_date][p_log_type][p_time]
        if not all_logs[p_date][p_log_type]:
            del all_logs[p_date][p_log_type]
            if not all_logs[p_date]: del all_logs[p_date]
        
        return F_Add_Log_File(all_logs)
    return False

# DESC: Deletes all logs older than the specified number of days.
def F_Del_Historical_Log(p_days_ago: int) -> bool:
    if not isinstance(p_days_ago, int) or p_days_ago < 0:
        print("Error: Days ago must be a non-negative integer")
        return False
        
    if p_days_ago == 0: return True
    try:
        all_logs = F_Get_Log_File()
        cutoff_date = L_Date.now() - L_Delta(days=p_days_ago)
        logs_to_keep = {}
        for date_str, logs in all_logs.items():
            try:
                log_date = L_Date.strptime(date_str, '%Y-%m-%d')
                if log_date >= cutoff_date: logs_to_keep[date_str] = logs
                else: print(f"Deleting logs for date: {date_str}")
            except ValueError:
                print(f"Warning: Invalid date format in logs: {date_str}")
                logs_to_keep[date_str] = logs
                
        if logs_to_keep != all_logs: return F_Add_Log_File(logs_to_keep)
        return True
    except Exception as e:
        print(f"Error deleting historical logs: {e}")
        return False
