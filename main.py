# ===== LIBRARY ========================================================================================================

import sys as L_SYS
import signal
import logging
import threading as L_Thread
from PyQt6.QtWidgets import QApplication as L_App, QMessageBox

from b_controller.controller import C_Main_Window
from c_service import d_telegram as S_Telegram
from d_model import d_telegram as M_Telegram

# ===== FUNCTION ========================================================================================================

def F_Start_Message():
    """Sends a startup message to all admin users"""
    admin_users = M_Telegram.F_Get_Admin_Users()
    if not admin_users:
        print("No admin users found.")
        return
    
    start_message = "🤖 Bybit Bot Started!\n\n The bot has started successfully. Click the button below to open the menu."
    control_buttons = {"📋 Menu": "/menu"}
    for user_id, user_data in admin_users.items():
        try: S_Telegram.F_Send_Button(user_id, start_message, control_buttons)
        except Exception as e: print(f"Failed to send message to {user_id}: {e}")

def F_Setup_Signal_Handlers():
    """Set up signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print("\nShutting down gracefully...")
        L_SYS.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def F_Main():
    """
    Main application function.
    Initializes the Telegram bot and desktop interface.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(), logging.FileHandler('bot.log')]
    )
    
    F_Setup_Signal_Handlers()
    try:
        F_Start_Message()
        logging.info("Startup message sent to admin users")
        bot_thread = L_Thread.Thread(target=S_Telegram.F_Start_Bot, name="TelegramBotThread", daemon=True)
        bot_thread.start()
        logging.info("Telegram bot thread started")
        app = L_App(L_SYS.argv)
        app.setApplicationName("Bybit Trading Bot")
        app.setApplicationVersion("1.0.0")
        try:
            window = C_Main_Window()
            window.show()
            logging.info("Main window displayed")
            return_code = app.exec()
            logging.info(f"Application exited with code: {return_code}")
        except Exception as e:
            logging.error(f"Error in PyQt application: {str(e)}", exc_info=True)
            QMessageBox.critical(
                None, "Application Error",
                f"An error occurred: {str(e)}\n\nCheck the log file for more details."
            )
            return 1
            
    except Exception as e:
        logging.critical(f"Fatal error during application startup: {str(e)}", exc_info=True)
        print(f"Fatal error: {str(e)}")
        return 1
    return 0

# ===== START ========================================================================================================

if __name__ == '__main__':
    sys.exit(F_Main())
