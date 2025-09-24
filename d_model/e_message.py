# ----- LIBRARY --------------------------------------------------

import json as L_JSON
import os as L_OS
from typing import Any, Dict, Optional, Union

# ----- LIBRARY --------------------------------------------------

# DESC: Path to the JSON file used as a message database.
MESSAGE_FILE_PATH = L_OS.path.join(L_OS.path.dirname(__file__), '..', 'e_database', 'e_message.json')

# ----- FUNCTION --------------------------------------------------

# DESC: Reads the message JSON file and returns its content as a dictionary.
def F_Get_Message_File() -> Dict[str, dict]:
    # DESC: Reads and parses the message JSON file.
    try:
        with open(MESSAGE_FILE_PATH, 'r', encoding='utf-8') as file_handle:
            message_data = L_JSON.load(file_handle)
            if not isinstance(message_data, dict): return {"message": {}, "button": {}}
            return {"message": message_data.get("message", {}), "button": message_data.get("button", {})}
    except (FileNotFoundError, L_JSON.JSONDecodeError) as e:
        print(f"Warning: Could not read message file: {e}")
        return {"message": {}, "button": {}}

# DESC: Writes the given dictionary structure to the Message JSON file.
def F_Add_Message_File(p_data: Dict[str, Any]) -> bool:
    try:
        os.makedirs(os.path.dirname(MESSAGE_FILE_PATH), exist_ok=True)
        temp_path = f"{MESSAGE_FILE_PATH}.tmp"
        with open(temp_path, 'w', encoding='utf-8') as file_handle: 
            L_JSON.dump(p_data, file_handle, indent=2, ensure_ascii=False)
        
        if os.path.exists(MESSAGE_FILE_PATH): os.remove(MESSAGE_FILE_PATH)
        os.rename(temp_path, MESSAGE_FILE_PATH)
        return True
    except (IOError, OSError, TypeError) as e:
        print(f"Error writing to message file: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try: os.remove(temp_path)
            except OSError: pass
        return False

# DESC: Retrieves the message text for the specified key.
def F_Get_Message(p_message_key: str) -> str:
    if not p_message_key: return "Error: Invalid message key"
    all_data = F_Get_Message_File()
    return all_data.get("message", {}).get(p_message_key, "Message not found.")

# DESC: Retrieves all messages as a dictionary.
def F_Get_All_Messages() -> Dict[str, str]:
    all_data = F_Get_Message_File()
    return all_data.get("message", {})

# DESC: Adds a new message or updates an existing one.
def F_Add_Message(p_key: str, p_value: str) -> bool:
    if not p_key or not isinstance(p_key, str):
        print("Error: Invalid message key")
        return False
        
    all_data = F_Get_Message_File()
    all_data["message"] = all_data.get("message", {})
    all_data["message"][p_key] = p_value
    return F_Add_Message_File(all_data)

# DESC: Deletes the message with the specified key.
def F_Del_Message(p_key: str) -> bool:
    if not p_key: return False
    all_data = F_Get_Message_File()
    if "message" in all_data and p_key in all_data["message"]:
        del all_data["message"][p_key]
        return F_Add_Message_File(all_data)
    return False

# DESC: Retrieves the buttons and commands for the specified menu name as a dictionary.
def F_Get_Button_Menu(p_menu_name: str) -> Dict[str, str]:
    if not p_menu_name: return {}
    all_data = F_Get_Message_File()
    return all_data.get("button", {}).get(p_menu_name, {})

# DESC: Retrieves all button menus.
def F_Get_All_Buttons() -> Dict[str, Dict[str, str]]:
    all_data = F_Get_Message_File()
    return all_data.get("button", {})

# DESC: Adds a new button to the specified menu or updates an existing one.
def F_Add_Button(p_menu_name: str, p_button_text: str, p_command: str) -> bool:
    if not all([p_menu_name, p_button_text, p_command]):
        print("Error: Menu name, button text, and command are required")
        return False
        
    if not all(isinstance(x, str) for x in [p_menu_name, p_button_text, p_command]):
        print("Error: Menu name, button text, and command must be strings")
        return False
        
    all_data = F_Get_Message_File()
    all_data["button"] = all_data.get("button", {})
    all_data["button"][p_menu_name] = all_data["button"].get(p_menu_name, {})
    all_data["button"][p_menu_name][p_button_text] = p_command
    return F_Add_Message_File(all_data)

# DESC: Deletes a button from the specified menu.
def F_Del_Button(p_menu_name: str, p_button_text: str) -> bool:
    if (not p_menu_name or not p_button_text or 
        not isinstance(p_menu_name, str) or 
        not isinstance(p_button_text, str)):
        return False
    try:
        all_data = F_Get_Message_File()
        if (all_data.get("button") and 
            p_menu_name in all_data["button"] and 
            p_button_text in all_data["button"][p_menu_name]):
            del all_data["button"][p_menu_name][p_button_text]
            if not all_data["button"][p_menu_name]: del all_data["button"][p_menu_name]
            return F_Add_Message_File(all_data)
    except Exception as e: print(f"Error in F_Del_Button: {e}")
    return False
