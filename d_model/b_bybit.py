# ----- LIBRARY --------------------------------------------------

import json as L_JSON
import os as L_OS

# ----- VARIABLE --------------------------------------------------

# DESC: Path to the JSON file used as the Bybit database.
BYBIT_FILE_PATH = L_OS.path.join(L_OS.path.dirname(__file__), '..', 'e_database', 'b_bybit.json')

# ----- FUNCTION --------------------------------------------------

# DESC: Sets the path of the Bybit JSON file and returns the new path.
def F_Add_Bybit_Path(p_path):
    global BYBIT_FILE_PATH
    BYBIT_FILE_PATH = p_path
    return BYBIT_FILE_PATH

# DESC: Returns the path of the configured Bybit JSON file.
def F_Get_Bybit_Path(): return BYBIT_FILE_PATH

# DESC: Reads the Bybit JSON file and returns its content as a dictionary.
def F_Get_Bybit_File():
    try:
        with open(BYBIT_FILE_PATH, 'r', encoding='utf-8') as file_handle:
            bybit_data = L_JSON.load(file_handle)
            return bybit_data
    except (FileNotFoundError, L_JSON.JSONDecodeError): return {"bot": {}, "setting": {}, "period": {}}

# DESC: Verilen sözlük yapısını Bybit JSON dosyasına yazar.
def F_Add_Bybit_File(p_data):
    try:
        with open(BYBIT_FILE_PATH, 'w', encoding='utf-8') as file_handle:
            L_JSON.dump(p_data, file_handle, indent=2, ensure_ascii=False)
            return True
    except Exception as local_error:
        print(f"Error writing to Bybit file: {local_error}")
        return False

# DESC: Retrieves the stored Bybit API and Secret keys.
def F_Get_Bot_Keys():
    bybit_data = F_Get_Bybit_File()
    return bybit_data.get("bot", {})

# DESC: Saves or updates the Bybit API and Secret keys.
def F_Add_Bot_Keys(p_api_key, p_secret_key):
    bybit_data = F_Get_Bybit_File()
    bybit_data["bot"] = {"main_api_key": p_api_key,"main_secret_key": p_secret_key}
    return F_Add_Bybit_File(bybit_data)

# DESC: Retrieves all settings as a dictionary.
def F_Get_Settings():
    bybit_data = F_Get_Bybit_File()
    return bybit_data.get("setting", {})

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
    all_data = F_Get_Bybit_File()
    settings = all_data.get("setting", {})
    if p_parity is not None: settings["parity"] = p_parity
    if p_min_leverage is not None: settings["min_leverage"] = p_min_leverage
    if p_min_volume is not None: settings["min_volume"] = p_min_volume
    if p_zigzag_period is not None: settings["zigzag_period"] = p_zigzag_period
    if p_period_1 is not None: settings["period_1"] = p_period_1
    if p_period_2 is not None: settings["period_2"] = p_period_2
    if p_max_volume is not None: settings["max_volume"] = p_max_volume
    if p_wait_time is not None: settings["wait_time"] = p_wait_time
    all_data["setting"] = settings
    return F_Add_Bybit_File(all_data)

# DESC: Retrieves all periods and their corresponding seconds.
def F_Get_All_Periods():
    bybit_data = F_Get_Bybit_File()
    return bybit_data.get("period", {})

# Alias for backward compatibility
F_Get_Period = F_Get_All_Periods

# DESC: Retrieves the seconds value of a specific period.
def F_Get_Period_Value(p_period_name):
    all_periods = F_Get_All_Periods()
    return all_periods.get(p_period_name)

# DESC: Adds or updates a period with its corresponding seconds value.
def F_Add_Period(p_period_name, p_seconds):
    all_data = F_Get_Bybit_File()
    if "period" not in all_data: all_data["period"] = {}
    all_data["period"][p_period_name] = p_seconds
    return F_Add_Bybit_File(all_data)

# DESC: Deletes the specified period.
def F_Del_Period(p_period_name):
    all_data = F_Get_Bybit_File()
    if "period" in all_data and p_period_name in all_data["period"]:
        del all_data["period"][p_period_name]
        return F_Add_Bybit_File(all_data)
    return False
