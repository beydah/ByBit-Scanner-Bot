# ----- HEADER --------------------------------------------------
# File: user_repository.py
# Description: Auto-generated header for structural compliance.

# ----- LIBRARY --------------------------------------------------

import json as L_JSON
from datetime import datetime as L_Date
from backend.core import database as DB

# ----- VARIABLE --------------------------------------------------

TELEGRAM_FILE_PATH = "SQLite Database"

# ----- FUNCTION --------------------------------------------------

def F_Add_Telegram_Path(p_path): pass
def F_Get_Telegram_Path(): return TELEGRAM_FILE_PATH

def F_Get_Telegram_File(): return {}
def F_Add_Telegram_File(p_data): return False

# DESC: Retrieves the stored Telegram bot token.
def F_Get_Bot_Token():
    return DB.kv_get('settings', 'telegram_bot_token')

# DESC: Saves or updates the Telegram bot token.
def F_Add_Bot_Token(p_token):
    DB.kv_set('settings', 'telegram_bot_token', p_token)
    return True

# DESC: Retrieves data for all users.
def F_Get_All_Users():
    conn = DB.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    
    users = {}
    for row in rows:
        users[row['user_id']] = {
            "user_name": row['user_name'],
            "user_type": bool(row['user_type']),
            "user_active": bool(row['user_active']),
            "user_add_date": row['user_add_date']
        }
    return users

# DESC: Retrieves all admin users.
def F_Get_Admin_Users():
    conn = DB.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_type = 1 AND user_active = 1")
    rows = cursor.fetchall()
    conn.close()
    
    admin_users = {}
    for row in rows:
        admin_users[row['user_id']] = {
            "user_name": row['user_name'],
            "user_type": True,
            "user_active": True,
            "user_add_date": row['user_add_date']
        }
    return admin_users

# DESC: Retrieves user data for the specified user ID.
def F_Get_User(p_user_id):
    conn = DB.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(p_user_id),))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "user_name": row['user_name'],
            "user_type": bool(row['user_type']),
            "user_active": bool(row['user_active']),
            "user_add_date": row['user_add_date']
        }
    return None

# DESC: Adds a new user.
def F_Add_User(p_user_id, p_user_name, p_user_type=False, p_user_active=True):
    user_id_str = str(p_user_id)
    # Check existence
    if F_Get_User(user_id_str): return False
    
    add_date = L_Date.now().strftime('%Y-%m-%d')
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, user_name, user_type, user_active, user_add_date) VALUES (?, ?, ?, ?, ?)",
            (user_id_str, p_user_name, 1 if p_user_type else 0, 1 if p_user_active else 0, add_date)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False

# DESC: Updates a user's information.
def F_Update_User(p_user_id, p_user_name=None, p_user_type=None, p_user_active=None):
    user_id_str = str(p_user_id)
    current_user = F_Get_User(user_id_str)
    if not current_user: return False
    
    updates = []
    params = []
    
    if p_user_name is not None:
        updates.append("user_name = ?")
        params.append(p_user_name)
    if p_user_type is not None:
        updates.append("user_type = ?")
        params.append(1 if p_user_type else 0)
    if p_user_active is not None:
        updates.append("user_active = ?")
        params.append(1 if p_user_active else 0)
        
    if not updates: return True
    
    params.append(user_id_str)
    query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
    
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating user: {e}")
        return False

# DESC: Deletes the user with the specified user ID.
def F_Del_User(p_user_id):
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (str(p_user_id),))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
