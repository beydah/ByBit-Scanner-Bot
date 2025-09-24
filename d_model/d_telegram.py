# ----- LIBRARY --------------------------------------------------

import json as L_JSON
import os as L_OS
from datetime import datetime as L_Date

# ----- VARIABLE --------------------------------------------------

# DESC: Path to the JSON file used as the Telegram database.
TELEGRAM_FILE_PATH = L_OS.path.join(L_OS.path.dirname(__file__), '..', 'e_database', 'd_telegram.json')

# ----- FUNCTION --------------------------------------------------

# DESC: Sets the path of the Telegram JSON file and returns the new path.
def F_Add_Telegram_Path(p_path):
    global TELEGRAM_FILE_PATH
    TELEGRAM_FILE_PATH = p_path
    return TELEGRAM_FILE_PATH

# DESC: Returns the path of the configured Telegram JSON file.
def F_Get_Telegram_Path(): return TELEGRAM_FILE_PATH

# DESC: Reads the Telegram JSON file and returns its content as a dictionary.
def F_Get_Telegram_File():
    try:
        with open(TELEGRAM_FILE_PATH, 'r', encoding='utf-8') as file_handle:
            telegram_data = L_JSON.load(file_handle)
            return telegram_data
    except (FileNotFoundError, L_JSON.JSONDecodeError): return {"bot": {}, "user": {}}

# DESC: Writes the given dictionary structure to the Telegram JSON file.
def F_Add_Telegram_File(p_data):
    try:
        with open(TELEGRAM_FILE_PATH, 'w', encoding='utf-8') as file_handle:
            L_JSON.dump(p_data, file_handle, indent=2, ensure_ascii=False)
            return True
    except Exception as local_error:
        print(f"Error writing to Telegram file: {local_error}")
        return False

# DESC: Retrieves the stored Telegram bot token.
def F_Get_Bot_Token():
    telegram_data = F_Get_Telegram_File()
    return telegram_data.get("bot", {}).get("bot_token")

# DESC: Saves or updates the Telegram bot token.
def F_Add_Bot_Token(p_token):
    telegram_data = F_Get_Telegram_File()
    if "bot" not in telegram_data: telegram_data["bot"] = {}
    telegram_data["bot"]["bot_token"] = p_token
    return F_Add_Telegram_File(telegram_data)

# DESC: Retrieves data for all users.
def F_Get_All_Users():
    telegram_data = F_Get_Telegram_File()
    return telegram_data.get("user", {})

# DESC: Retrieves all admin users.
def F_Get_Admin_Users():
    all_users = F_Get_All_Users()
    admin_users = {}
    for user_id, user_data in all_users.items():
        if user_data.get("user_type", False) and user_data.get("user_active", True):
            admin_users[user_id] = user_data
    return admin_users

# DESC: Retrieves user data for the specified user ID.
def F_Get_User(p_user_id):
    all_users = F_Get_All_Users()
    return all_users.get(str(p_user_id))

# DESC: Adds a new user.
def F_Add_User(p_user_id, p_user_name, p_user_type=False, p_user_active=True):
    all_data = F_Get_Telegram_File()
    user_id_str = str(p_user_id)
    if "user" not in all_data: all_data["user"] = {}
    if user_id_str in all_data["user"]: return False 
    all_data["user"][user_id_str] = {
        "user_name": p_user_name,
        "user_type": p_user_type,
        "user_active": p_user_active,
        "user_add_date": L_Date.now().strftime('%Y-%m-%d')
    }
    return F_Add_Telegram_File(all_data)

# DESC: Updates a user's information.
def F_Update_User(p_user_id, p_user_name=None, p_user_type=None, p_user_active=None):
    all_data = F_Get_Telegram_File()
    user_id_str = str(p_user_id)
    if "user" not in all_data or user_id_str not in all_data["user"]: return False
    user_data = all_data["user"][user_id_str]
    if p_user_name is not None: user_data["user_name"] = p_user_name
    if p_user_type is not None: user_data["user_type"] = p_user_type
    if p_user_active is not None: user_data["user_active"] = p_user_active
    return F_Add_Telegram_File(all_data)

# DESC: Deletes the user with the specified user ID.
def F_Del_User(p_user_id):
    all_data = F_Get_Telegram_File()
    user_id_str = str(p_user_id)
    if "user" in all_data and user_id_str in all_data["user"]:
        del all_data["user"][user_id_str]
        return F_Add_Telegram_File(all_data)
    return False
