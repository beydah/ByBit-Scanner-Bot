# ----- HEADER --------------------------------------------------

# File: config.py
# Description: Auto-generated header for structural compliance.

# ----- LIBRARY --------------------------------------------------

import os as L_OS
from dotenv import load_dotenv as L_Load_Dotenv
from backend.core import database as DB

# Load environment variables from .env file
L_Load_Dotenv()

# ----- VALIDATION --------------------------------------------------

def F_Validate_Environment():
    """
    Validates that essential environment variables are set.
    """
    required_keys = [
        "BYBIT_MAIN_API_KEY", 
        "BYBIT_MAIN_SECRET_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_USER_ID"
    ]
    missing = [key for key in required_keys if not L_OS.getenv(key)]
    
    if missing:
        print(f"CRITICAL: Missing environment variables: {', '.join(missing)}")
        print("Please check your .env file.")
        return False
    return True

# Initialize validation
if not F_Validate_Environment():
    # We don't exit here to allow the GUI to potentially show an error, 
    # but core services should check this.
    pass

# ----- VARIABLE --------------------------------------------------

# Cache for settings to avoid db hits on every read
_settings_cache = None
_period_cache = None

# ----- FUNCTION --------------------------------------------------

# Legacy Path Functions (kept for compatibility but no-op or specific usage)
def F_Add_Bybit_Path(p_path): pass
def F_Get_Bybit_Path(): return "SQLite Database"

# DESC: Retrieves Telegram Bot Token and User ID from environment.
def F_Get_Telegram_Keys():
    token = L_OS.getenv("TELEGRAM_BOT_TOKEN")
    user_id = L_OS.getenv("TELEGRAM_USER_ID")
    return {"token": token, "user_id": user_id}

# DESC: Retrieves the stored Bybit API and Secret keys.
# PRIORITY: Environment Variables ONLY now (for security)
def F_Get_Bot_Keys():
    api_key = L_OS.getenv("BYBIT_MAIN_API_KEY")
    secret_key = L_OS.getenv("BYBIT_MAIN_SECRET_KEY")
    
    if api_key and secret_key:
        return {"main_api_key": api_key, "main_secret_key": secret_key}
    
    # Fallback to empty dict if not set
    return {}

# DESC: Saves or updates the Bybit API and Secret keys.
# NOW: Reminds user to use .env
def F_Add_Bot_Keys(p_api_key, p_secret_key):
    print("WARNING: Saving keys to file is deprecated. Please set BYBIT_MAIN_API_KEY and BYBIT_MAIN_SECRET_KEY in .env file.")
    return False

# DESC: Retrieves all settings as a dictionary.
def F_Get_Settings():
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = DB.kv_get_all('settings')
    return _settings_cache

# DESC: Updates settings. Only non-None values will be updated.
def F_Update_Settings(
        p_parity=None, 
        p_min_leverage=None, 
        p_min_volume=None, 
        p_zigzag_period=None, 
        p_period_1=None, 
        p_period_2=None, 
        p_max_volume=None, 
        p_wait_time=None
        ):
    global _settings_cache
    
    # Update Cache first
    if _settings_cache is None: _settings_cache = F_Get_Settings()
    
    updates = {
        "parity": p_parity,
        "min_leverage": p_min_leverage,
        "min_volume": p_min_volume,
        "zigzag_period": p_zigzag_period,
        "period_1": p_period_1,
        "period_2": p_period_2,
        "max_volume": p_max_volume,
        "wait_time": p_wait_time
    }
    
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        
        for key, value in updates.items():
            if value is not None:
                _settings_cache[key] = value
                # Store as plain value or JSON string depending on type?
                # DB kv_set handles JSON dumping.
                # But here we want to do it transactionally/efficiently?
                # Let's just use kv_set for simplicity or direct query
                import json
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                               (key, json.dumps(value, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating settings: {e}")
        return False

# DESC: Retrieves all periods and their corresponding seconds.
def F_Get_All_Periods():
    global _period_cache
    if _period_cache is None:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, seconds FROM periods")
        rows = cursor.fetchall()
        conn.close()
        _period_cache = {row['name']: str(row['seconds']) for row in rows}
    return _period_cache

# Alias for backward compatibility
F_Get_Period = F_Get_All_Periods

# DESC: Retrieves the seconds value of a specific period.
def F_Get_Period_Value(p_period_name):
    all_periods = F_Get_All_Periods()
    return all_periods.get(p_period_name)

# DESC: Adds or updates a period with its corresponding seconds value.
def F_Add_Period(p_period_name, p_seconds):
    global _period_cache
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO periods (name, seconds) VALUES (?, ?)", (p_period_name, p_seconds))
        conn.commit()
        conn.close()
        
        # Update cache
        if _period_cache is None: _period_cache = {}
        _period_cache[p_period_name] = str(p_seconds)
        return True
    except Exception as e:
        print(f"Error adding period: {e}")
        return False

# DESC: Deletes the specified period.
def F_Del_Period(p_period_name):
    global _period_cache
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM periods WHERE name = ?", (p_period_name,))
        conn.commit()
        conn.close()
        
        if _period_cache and p_period_name in _period_cache:
            del _period_cache[p_period_name]
        return True
    except Exception as e:
        print(f"Error deleting period: {e}")
        return False
