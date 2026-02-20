# ----- HEADER --------------------------------------------------
# File: headless_main.py
# Description: Auto-generated header for structural compliance.

import sys
import time
import logging
import threading
from backend.notification import telegram_service as S_Telegram
from backend.market import scanner_engine as S_Scanner

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_headless.log')
    ]
)

def main():
    """
    Headless entry point for the bot (Docker/Server).
    Runs without GUI keys.
    """
    logging.info("Starting Bybit Bot in HEADLESS mode...")
    
    # 1. Start Telegram Bot
    try:
        telegram_thread = threading.Thread(target=S_Telegram.F_Start_Bot, name="TelegramBot", daemon=True)
        telegram_thread.start()
        logging.info("Telegram Bot started.")
    except Exception as e:
        logging.critical(f"Failed to start Telegram Bot: {e}")
        return 1

    # 2. Start Scanner
    try:
        # F_Start_Scanner starts its own thread
        result = S_Scanner.F_Start_Scanner()
        if result.get("status") == "success":
             logging.info("Scanner started.")
        else:
             logging.error(f"Scanner failed to start: {result.get('message')}")
    except Exception as e:
        logging.critical(f"Failed to start Scanner: {e}")
        return 1

    # 3. Main Loop (Keep alive)
    try:
        while True:
            # Drain queue to prevent memory leak since no GUI is consuming it
            items_cleared = 0
            while not S_Scanner.S_Signal_Que.empty():
                try: 
                    S_Scanner.S_Signal_Que.get_nowait()
                    items_cleared += 1
                except: pass
            
            if items_cleared > 0:
                logging.debug(f"Cleared {items_cleared} signals from queue.")

            status = S_Scanner.F_Get_Status_Scanner()
            logging.info(f"Heartbeat: {status.get('status')} | Symbols Scanned: {status.get('scanned_symbols')}")
            time.sleep(60)
            
    except KeyboardInterrupt:
        logging.info("Stopping bot...")
        S_Scanner.F_Stop_Scanner()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
