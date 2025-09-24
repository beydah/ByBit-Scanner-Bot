# ===== LIBRARY ========================================================================================================

import sys as L_SYS
import os as L_OS
import time as L_Time
import threading as L_Thread
from datetime import datetime as L_Date
from typing import Dict, Any, Optional

from c_service import c_scanner as S_Scanner
from c_service import d_telegram as S_Telegram
from d_model import b_bybit as M_Bybit
from d_model import e_message as M_Message
from d_model import d_telegram as M_Telegram
from d_model import f_log as M_Log

# ===== VARIABLE ======================================================================================

L_SYS.path.append(L_OS.path.dirname(L_OS.path.dirname(L_OS.path.abspath(__file__))))
User_States: Dict[str, Dict[str, Any]] = {}
User_States_Lock = L_Thread.Lock()
Last_Cleanup_Time = L_Time.time()
STATE_EXPIRY_HOURS = 24
STATE_CLEANUP_INTERVAL = 3600

# ===== FUNCTIONS =============================================================================================

def F_Get_Admins() -> list:
    # DESC: Returns a list of all admin user IDs in the system.
    all_users = M_Telegram.F_Get_All_Users()
    return [uid for uid, data in all_users.items() if data.get("user_type")]

def F_Format_Log(logs: dict) -> str:
    # DESC: Converts log data into a readable text format.
    if not logs: return "No logs found to display."
    log_text = ""
    for log_time, log_data in logs.items():
        log_text += f"⏰ [{log_time}] - *{log_data['title']}*\n"
        log_text += f"```{log_data['description']}```\n\n"
    return log_text

def F_Set_User_State(user_id: str, state: str, data: Any = None):
    with User_States_Lock:
        User_States[str(user_id)] = {'state': state, 'timestamp': L_Time.time(), 'data': data}
        if L_Time.time() - Last_Cleanup_Time > STATE_CLEANUP_INTERVAL: F_Cleanup_User_States()

def F_Get_User_State(user_id: str) -> Optional[Dict[str, Any]]:
    with User_States_Lock: return User_States.get(str(user_id))

def F_Clear_User_State(user_id: str):
    with User_States_Lock: User_States.pop(str(user_id), None)

def F_Cleanup_User_States():
    global Last_Cleanup_Time
    with User_States_Lock:
        expiry_time = L_Time.time() - (STATE_EXPIRY_HOURS * 3600)
        expired_ids = [uid for uid, data in User_States.items() if data.get('timestamp', 0) < expiry_time]
        for user_id in expired_ids: User_States.pop(user_id, None)
        Last_Cleanup_Time = L_Time.time()

def F_Transaction(user_id: str, user_name: str, text: str):
    # DESC: Main function that processes all messages and commands from the user.
    user_id = str(user_id)
    state_info = F_Get_User_State(user_id)
    if not M_Telegram.F_Get_User(user_id):
        is_admin = user_id in F_Get_Admins()
        M_Telegram.F_Add_User(user_id, user_name, p_user_type=is_admin, p_user_active=True)
    
    if state_info: F_Handle_Waiting_State(user_id, user_name, text, state_info)
    else: F_Handle_Command(user_id, user_name, text)

def F_Handle_Waiting_State(user_id: str, user_name: str, text: str, state_info: Dict):
    # DESC: Manages inputs from users who are waiting for a response.
    state = state_info.get('state')
    if text.lower() == '/exit':
        F_Clear_User_State(user_id)
        S_Telegram.F_Send_Message(user_id, "Operation cancelled.")
        return

    try:
        if state == "waiting_period_selection":
            if text.startswith("set_period_"):
                period_value = text.replace("set_period_", "")
                target_period = state_info.get('data')
                try:
                    update_result = M_Bybit.F_Update_Settings(**{f"p_period_{target_period}": period_value})
                    if update_result:
                        S_Telegram.F_Send_Message(user_id, f"✅ Period {target_period} successfully updated: {period_value}")
                        M_Log.F_Add_Log('transaction', 'SettingUpdate', f"User {user_name} updated period {target_period} setting: {period_value}")
                    
                    else:
                        S_Telegram.F_Send_Message(user_id, f"❌ An error occurred while updating the period! (Value: {period_value})")
                        M_Log.F_Add_Log('error', 'PeriodUpdateError', f"Failed to update period {target_period} for user {user_name}. Value: {period_value}")
                except Exception as e:
                    S_Telegram.F_Send_Message(user_id, f"❌ An unexpected error occurred while updating the period! {str(e)}")
                    M_Log.F_Add_Log('error', 'PeriodUpdateException', f"Failed to update period {target_period} for user {user_name}. Error: {str(e)} Value: {period_value}")
                finally:
                    F_Clear_User_State(user_id)
                    all_message_data = M_Message.F_Get_Message_File()
                    messages = all_message_data.get('message', {})
                    buttons = all_message_data.get('button', {})
                    S_Telegram.F_Send_Button(user_id, messages.get('menu', 'Main Menu'), buttons.get('menu'))
                return
            else:
                S_Telegram.F_Send_Message(user_id, "Invalid period selection. Please select one of the buttons.")
                return
            
        if state.startswith("waiting_"):
            setting_key = state.replace("waiting_", "")
            value = text
            if setting_key in ["min_leverage", "min_volume", "zigzag_period"]:
                try: value = int(text)
                except ValueError:
                    S_Telegram.F_Send_Message(user_id, "Invalid input. Please enter a numeric value.")
                    return
            
            M_Bybit.F_Update_Settings(**{f"p_{setting_key}": value})
            S_Telegram.F_Send_Message(user_id, f"✅ Setting '{setting_key}' successfully updated.")
            M_Log.F_Add_Log('transaction', 'SettingUpdate', f"User {user_name} updated setting: {setting_key} -> {value}")
        else:
            S_Telegram.F_Send_Message(user_id, "Invalid state, operation reset.")
            pass
        
        F_Clear_User_State(user_id)
    except Exception as e:
        M_Log.F_Add_Log('error', 'HandleWaitingStateError', str(e))
        S_Telegram.F_Send_Message(user_id, "An error occurred, operation cancelled.")
        F_Clear_User_State(user_id)

def F_Handle_Command(user_id: str, user_name: str, command: str):
    # DESC: Manages direct incoming commands.
    all_message_data = M_Message.F_Get_Message_File()
    messages = all_message_data.get('message', {})
    buttons = all_message_data.get('button', {})
    is_admin = user_id in F_Get_Admins()
    admin_commands = [
        "/bot_start", "/bot_stop", "/set_setting_menu", "/set_parity", 
        "/set_leverage", "/set_min_volume", "/set_max_volume", "/set_zigzag_period",
        "/set_period_1", "/set_period_2", "/set_wait_time", "/get_user_menu", 
        "/get_admin_menu", "/get_error", "/get_alert", "/get_transaction"
    ]
    if command in admin_commands and not is_admin:
        S_Telegram.F_Send_Message(user_id, messages.get('denied'))
        return

    try:
        # Check button callbacks
        if command == '/menu' or command == 'menu': S_Telegram.F_Send_Button(user_id, messages.get('menu', 'Ana Menü'), buttons.get('menu'))
        elif command == '/start': S_Telegram.F_Send_Button(user_id, messages.get('start'), buttons.get('start_menu'))
        elif command == '/exit': 
            current_state = F_Get_User_State(user_id)
            if current_state:
                F_Clear_User_State(user_id)
                S_Telegram.F_Send_Message(user_id, messages.get('exited', 'İşlem iptal edildi.'))
                S_Telegram.F_Send_Button(user_id, messages.get('menu', 'Ana Menü'), buttons.get('menu'))

            else: S_Telegram.F_Send_Button(user_id, messages.get('menu', 'Ana Menü'), buttons.get('menu'))

        elif command == "open_dashboard": S_Telegram.F_Send_Message(user_id, "📊 Dashboard will open in the desktop application.")
        elif command == "scanner_status":
            status_info = S_Scanner.F_Get_Status_Scanner()
            status = status_info.get("status", "stopped").upper()
            status_msg = f"🔄 Scanner Status: {status}\n\n"
            status_msg += f"📊 Statistics:\n"
            status_msg += f"• Total Symbols: {status_info.get('total_symbols', 0)}\n"
            status_msg += f"• Scanned Symbols: {status_info.get('scanned_symbols', 0)}\n"
            status_msg += f"• Found Signals: {status_info.get('found_signals', 0)}\n"
            status_msg += f"• Current Symbol: {status_info.get('current_symbol', '-')}\n"
            status_msg += f"• Current Period: {status_info.get('current_period', '-')}"
            S_Telegram.F_Send_Message(user_id, status_msg)

        elif command == "settings":
            settings = M_Bybit.F_Get_Settings()
            settings_msg = "⚙️ Current Settings:\n\n"
            for key, value in settings.items(): settings_msg += f"• {key.replace('_', ' ').title()}: {value}\n"
            S_Telegram.F_Send_Message(user_id, settings_msg)

        elif command == "logs":
            today_str = L_Date.now().strftime('%Y-%m-%d')
            logs = M_Log.F_Get_Log(today_str)
            if not logs:
                S_Telegram.F_Send_Message(user_id, "No logs found for today.")
                return

            formatted_logs = F_Format_Log(logs)
            S_Telegram.F_Send_Message(user_id, formatted_logs, parse_mode='Markdown')

        elif command == '/bot_start':
            result = S_Scanner.F_Start_Scanner()
            S_Telegram.F_Send_Message(user_id, result.get('message'))

        elif command == '/bot_stop':
            result = S_Scanner.F_Stop_Scanner()
            S_Telegram.F_Send_Message(user_id, result.get('message'))

        elif command == '/get_setting':
            settings = M_Bybit.F_Get_Settings()
            settings_msg = "⚙️ Current Settings:\n" + "\n".join([f"🔹 {k.replace('_', ' ').title()}: {v}" for k, v in settings.items()])
            S_Telegram.F_Send_Message(user_id, settings_msg)

        elif command == '/set_setting_menu' or command == '/set_setting':
            S_Telegram.F_Send_Button(user_id, messages.get('setting_menu', 'Which setting would you like to change?'), buttons.get('setting_menu'))

        elif command == '/get_user_menu':
            S_Telegram.F_Send_Button(user_id, messages.get('user_menu', 'User operations menu:'), buttons.get('user_menu'))

        elif command == '/get_admin_menu':
            S_Telegram.F_Send_Button(user_id, messages.get('admin_menu', 'Admin operations menu:'), buttons.get('admin_menu'))

        elif command == '/set_parity':
            F_Set_User_State(user_id, "waiting_parity")
            S_Telegram.F_Send_Message(user_id, "Please enter the new parity (e.g., USDT):")

        elif command == '/set_leverage':
            F_Set_User_State(user_id, "waiting_min_leverage")
            S_Telegram.F_Send_Message(user_id, "Please enter the new minimum leverage value:")

        elif command == '/set_min_volume':
            F_Set_User_State(user_id, "waiting_min_volume")
            S_Telegram.F_Send_Message(user_id, "Please enter the new minimum 24h volume value:")

        elif command == '/set_max_volume':
            F_Set_User_State(user_id, "waiting_max_volume")
            S_Telegram.F_Send_Message(user_id, "Please enter the new maximum 24h volume value:")

        elif command == '/set_zigzag_period':
            F_Set_User_State(user_id, "waiting_zigzag_period")
            S_Telegram.F_Send_Message(user_id, "Please enter the new ZigZag period:")

        elif command == '/set_period_1':
            F_Set_User_State(user_id, "waiting_period_selection", "1")
            S_Telegram.F_Send_Button(user_id, messages.get('set_period_1'), buttons.get('period_menu'))

        elif command == '/set_period_2':
            F_Set_User_State(user_id, "waiting_period_selection", "2")
            S_Telegram.F_Send_Button(user_id, messages.get('set_period_2'), buttons.get('period_menu'))

        elif command.startswith('set_period_'):
            period_value = command.replace('set_period_', '')
            current_state = F_Get_User_State(user_id)
            if current_state and current_state.get('state') == 'waiting_period_selection':
                target_period = current_state.get('data')
                try:
                    update_result = M_Bybit.F_Update_Settings(**{f"p_period_{target_period}": period_value})
                    if update_result:
                        S_Telegram.F_Send_Message(user_id, f"✅ Periyot {target_period} başarıyla güncellendi: {period_value}")
                        M_Log.F_Add_Log('transaction', 'SettingUpdate', f"Kullanıcı {user_name} periyot {target_period} ayarını güncelledi: {period_value}")
                    
                    else:
                        S_Telegram.F_Send_Message(user_id, f"❌ Periyot güncellenirken bir hata oluştu! (Değer: {period_value})")
                        M_Log.F_Add_Log('error', 'PeriodUpdateError', f"Kullanıcı {user_name} için periyot {target_period} güncellenemedi. Değer: {period_value}")
                
                except Exception as e:
                    S_Telegram.F_Send_Message(user_id, f"❌ Periyot güncellenirken beklenmeyen bir hata oluştu! {str(e)}")
                    M_Log.F_Add_Log('error', 'PeriodUpdateException', f"Kullanıcı {user_name} için periyot {target_period} güncellenemedi. Hata: {str(e)} Değer: {period_value}")
                
                finally:
                    F_Clear_User_State(user_id)
                    S_Telegram.F_Send_Button(user_id, messages.get('menu', 'Ana Menü'), buttons.get('menu'))

            else:
                S_Telegram.F_Send_Message(user_id, f"❌ Invalid state for period selection. (State: {current_state})")
                M_Log.F_Add_Log('error', 'PeriodStateError', f"Invalid state for user {user_name}: {current_state}")
                F_Clear_User_State(user_id)
                S_Telegram.F_Send_Button(user_id, messages.get('menu', 'Ana Menü'), buttons.get('menu'))

        elif command == '/set_wait_time':
            F_Set_User_State(user_id, "waiting_wait_time")
            S_Telegram.F_Send_Message(user_id, "Please enter the new wait time (e.g., 10M):")

        elif command in ['/get_error', '/get_alert', '/get_transaction']:
            log_type = command.replace('/get_', '')
            today_str = L_Date.now().strftime('%Y-%m-%d')
            logs = M_Log.F_Get_Log(today_str, log_type)
            if not logs:
                S_Telegram.F_Send_Message(user_id, messages.get('no_logs_found').format(log_type=log_type))
                return

            formatted_logs = F_Format_Log(logs)
            S_Telegram.F_Send_Message(user_id, formatted_logs, parse_mode='Markdown')
        else: S_Telegram.F_Send_Message(user_id, messages.get('unknown'))
            
    except Exception as e:
        M_Log.F_Add_Log('error', 'HandleCommandError', str(e))
        S_Telegram.F_Send_Message(user_id, "An error occurred while processing the command.")
