# ----- HEADER --------------------------------------------------

# File: telegram_service.py
# Description: Auto-generated header for structural compliance.

# ----- LIBRARY --------------------------------------------------

import os as L_OS
import sys as L_SYS

import time as L_Time
import requests as L_Requests
import threading as L_Threading

from telebot import TeleBot as L_Telebot
from typing import Dict, Any, Optional

from c_service import e_transaction as S_Transaction
from backend.core import config as M_Bybit
from backend.logger import log_service as M_Log
from backend.notification import user_repository as M_Telegram

# ----- VARIABLE --------------------------------------------------

_keys = M_Bybit.F_Get_Telegram_Keys()
BOT_TOKEN = _keys.get("token")
ADMIN_USER_ID = _keys.get("user_id")
BOT = L_Telebot(BOT_TOKEN)

# ----- FUNCTION --------------------------------------------------

def F_Send_Message(chat_id: str, text: str, parse_mode: Optional[str] = None) -> bool:
    # DESC: Sends a text message to the specified chat ID.
    while True:
        try:
            BOT.send_message(chat_id, text, parse_mode=parse_mode)
            return True
        except L_Requests.exceptions.RequestException as e:
            M_Log.F_Add_Log('error', 'SendMessageError', f"ChatID: {chat_id} - Network Error: {str(e)}")
            L_Time.sleep(60)
            continue
        except Exception as e:
            M_Log.F_Add_Log('error', 'SendMessageError', f"ChatID: {chat_id} - Error: {str(e)}")
            return False

def F_Send_Button(chat_id: str, text: str, buttons: Dict[str, str]) -> bool:
    # DESC: Sends a message with inline buttons to the specified chat ID. Buttons are arranged in groups of 3.
    while True:
        try:
            from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup()
            button_items = list(buttons.items())
            for i in range(0, len(button_items), 3):
                row = [InlineKeyboardButton(txt, callback_data=data) for txt, data in button_items[i:i+3]]
                keyboard.row(*row)

            BOT.send_message(chat_id, text, reply_markup=keyboard)
            return True
        except L_Requests.exceptions.RequestException as e:
            M_Log.F_Add_Log('error', 'SendButtonError', f"ChatID: {chat_id} - Network Error: {str(e)}")
            L_Time.sleep(60)
            continue
        except Exception as e:
            M_Log.F_Add_Log('error', 'SendButtonError', f"ChatID: {chat_id} - Error: {str(e)}")
            return False

def _process_messages(messages):
    # DESC: Processes incoming messages or callbacks.
    for msg in messages:
        try:
            if hasattr(msg, 'data'):  # This is a callback query (button click)
                user_id = str(msg.from_user.id)
                user_name = msg.from_user.first_name
                text = msg.data
                BOT.answer_callback_query(msg.id)  # Acknowledge button press to Telegram
            else:  # This is a regular message
                user_id = str(msg.from_user.id)
                user_name = msg.from_user.first_name
                text = msg.text

            S_Transaction.F_Transaction(user_id, user_name, text)
        except Exception as e: M_Log.F_Add_Log('error', 'MessageProcessError', str(e))

@BOT.message_handler(func=lambda message: True)
def _handle_all_messages(message):
    # DESC: Catches all incoming messages.
    _process_messages([message])

@BOT.callback_query_handler(func=lambda call: True)
def _handle_all_callbacks(call):
    # DESC: Catches all button clicks (callbacks).
    _process_messages([call])

def F_Start_Bot():
    # DESC: Starts the Telegram bot using polling method and automatically restarts on errors.
    def run():
        while True:
            try:
                M_Log.F_Add_Log('transaction', 'BotStart', 'Telegram bot started with polling method.')
                BOT.polling(none_stop=True, interval=0, timeout=60)
            except L_Requests.exceptions.RequestException as e:
                print(f"Bot polling network error: {e}. Retrying in 60 seconds...")
                M_Log.F_Add_Log('error', 'BotPollingError', f"Network Error: {str(e)}. Bot will restart in 60 seconds.")
                L_Time.sleep(60)
                continue
            except Exception as e:
                print(f"Bot polling error: {e}. Restarting...")
                M_Log.F_Add_Log('error', 'BotPollingError', f"Error: {str(e)}. Bot will restart in 10 seconds.")
                L_Time.sleep(10)
                continue
    bot_thread = L_Threading.Thread(target=run, daemon=True)
    bot_thread.start()
