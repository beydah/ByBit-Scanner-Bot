# ----- HEADER --------------------------------------------------
# File: message_repository.py
# Description: Auto-generated header for structural compliance.

# ----- LIBRARY --------------------------------------------------

import json as L_JSON
from typing import Any, Dict, Optional, Union
from backend.core import database as DB

# ----- VARIABLE --------------------------------------------------

MESSAGE_FILE_PATH = "SQLite Database"

# ----- FUNCTION --------------------------------------------------

def F_Get_Message_File() -> Dict[str, dict]: return {}
def F_Add_Message_File(p_data: Dict[str, Any]) -> bool: return False

# DESC: Retrieves the message text for the specified key.
def F_Get_Message(p_message_key: str) -> str:
    if not p_message_key: return "Error: Invalid message key"
    # Using specific table 'messages' via custom query, or potentially generic KV if structure matches?
    # db.init_db created 'messages' table: key, value (TEXT)
    # So we can use DB.kv_get but we need to specify table? No kv_get is generic
    # wait, DB.kv_get takes 'table' arg.
    return DB.kv_get('messages', p_message_key, "Message not found.")

# DESC: Retrieves all messages as a dictionary.
def F_Get_All_Messages() -> Dict[str, str]:
    return DB.kv_get_all('messages')

# DESC: Adds a new message or updates an existing one.
def F_Add_Message(p_key: str, p_value: str) -> bool:
    if not p_key: return False
    DB.kv_set('messages', p_key, p_value)
    return True

# DESC: Deletes the message with the specified key.
def F_Del_Message(p_key: str) -> bool:
    if not p_key: return False
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE key = ?", (p_key,))
        conn.commit()
        conn.close()
        return True
    except: return False

# DESC: Retrieves the buttons and commands for the specified menu name as a dictionary.
def F_Get_Button_Menu(p_menu_name: str) -> Dict[str, str]:
    conn = DB.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT button_text, command FROM buttons WHERE menu_name = ?", (p_menu_name,))
    rows = cursor.fetchall()
    conn.close()
    
    return {row['button_text']: row['command'] for row in rows}

# DESC: Retrieves all button menus.
def F_Get_All_Buttons() -> Dict[str, Dict[str, str]]:
    conn = DB.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT menu_name, button_text, command FROM buttons")
    rows = cursor.fetchall()
    conn.close()
    
    result = {}
    for row in rows:
        menu = row['menu_name']
        if menu not in result: result[menu] = {}
        result[menu][row['button_text']] = row['command']
    return result

# DESC: Adds a new button to the specified menu or updates an existing one.
def F_Add_Button(p_menu_name: str, p_button_text: str, p_command: str) -> bool:
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO buttons (menu_name, button_text, command) VALUES (?, ?, ?)",
            (p_menu_name, p_button_text, p_command)
        )
        conn.commit()
        conn.close()
        return True
    except: return False

# DESC: Deletes a button from the specified menu.
def F_Del_Button(p_menu_name: str, p_button_text: str) -> bool:
    try:
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM buttons WHERE menu_name = ? AND button_text = ?",
            (p_menu_name, p_button_text)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error F_Del_Button: {e}")
        return False
