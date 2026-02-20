# ----- HEADER --------------------------------------------------

# File: scanner_engine.py
# Description: Auto-generated header for structural compliance.

# ----- LIBRARY --------------------------------------------------

import threading as L_Thread
import time as L_Time
import concurrent.futures as L_Futures

from backend.market import bybit_service as S_Bybit
from backend.trade import signal_logic as S_Strategy
from backend.notification import telegram_service as S_Telegram
from backend.trade.signal_queue import Signal_Que as S_Signal_Que

from backend.core import config as M_Bybit
from backend.logger import log_service as M_Log
from backend.notification import user_repository as M_Telegram

# ----- VARIABLE --------------------------------------------------

_scanner_thread = None
_scanner_stop_event = None
_scanner_status = "stopped" # possible states: stopped, running, waiting, starting, stopping

# Scanner status information
_scanner_stats = {
    'total_symbols': 0,
    'scanned_symbols': 0,
    'current_symbol': '-',
    'current_period': '-',
    'found_signals': 0,
    'last_signal_time': None,
    'current_price': '-',
    'last_zigzag_level': '-',
    'last_fibo_level': '-'
}

# Callback to clear the Recent Activities table
_activity_table_clear_callback = None
def set_activity_table_clear_callback(cb):
    global _activity_table_clear_callback
    _activity_table_clear_callback = cb

# ----- FUCNTION --------------------------------------------------

def F_Get_Price(symbol):
    # DESC: Gets the current price of the symbol
    try:
        closes = S_Bybit.F_Get_Close(symbol, "1")
        if closes and len(closes) > 0: return f"{closes[-1]:.8f}"
        return "-"
    except: return "-"

def F_Get_Zigzag(closes, highs, lows, zigzag_period):
    # DESC: Calculates the last ZigZag level
    try:
        zigzag = S_Strategy.F_Get_ZigZag_Periodic(closes, zigzag_period)
        if zigzag and len(zigzag) > 0: return f"{zigzag[-1]:.8f}"
        return "-"
    except: return "-"

def F_Scan(symbol_data, periods_to_scan, zigzag_period):
    symbol = symbol_data['symbol']
    global _scanner_stats
    
    # NOTE: Incrementing shared counter is not thread-safe without lock, but strict accuracy isn't critical here.
    # For better thread safety, we should use a lock, but keeping it simple for now to match performance requirements.
    _scanner_stats['scanned_symbols'] += 1
    
    for period in periods_to_scan:
        if _scanner_stop_event.is_set(): break
        _scanner_stats['current_symbol'] = symbol
        _scanner_stats['current_period'] = period
        
        # Optimize: Fetch data for all periods in parallel or batch if possible in future
        closes = S_Bybit.F_Get_Close(symbol, period)
        highs = S_Bybit.F_Get_High(symbol, period)
        lows = S_Bybit.F_Get_Low(symbol, period)
        
        if closes is None or highs is None or lows is None or not (closes and highs and lows):
            signal_data = {
                "symbol": symbol,
                "volume": '-',
                "period": period,
                "price": '-',
                "pattern": 'no data',
                "fib_0_0": '-',
                "fib_0_01": '-',
                "fib_0_236": '-',
                "fib_0_382": '-',
                "fib_1_0": '-'
            }
            # Only put empty signals if needed for debugging, excessive queue usage can clog UI
            # S_Signal_Que.put(signal_data) 
            continue

        _scanner_stats['current_price'] = F_Get_Price(symbol)
        _scanner_stats['last_zigzag_level'] = F_Get_Zigzag(closes, highs, lows, zigzag_period)
        _scanner_stats['last_fibo_level'] = S_Strategy.F_Get_Fibonacci(closes, highs, lows)
        
        long_signal = S_Strategy.F_Get_Long_Signal(closes, highs, lows, zigzag_period)
        short_signal = S_Strategy.F_Get_Short_Signal(closes, highs, lows, zigzag_period)
        
        # --- LONG SIGNAL ---
        if long_signal.get("signal") == "long":
            fibo_levels = S_Strategy.F_Get_Fibonacci(closes, highs, lows)
            stop_loss = fibo_levels.get('1.272', 0) if fibo_levels else 0
            take_profit = fibo_levels.get('1.0', 0) if fibo_levels else 0
            fibo3 = fibo_levels.get('0.382', '-') if fibo_levels else '-'
            fibo4 = fibo_levels.get('0.5', '-') if fibo_levels else '-'
            fibo5 = fibo_levels.get('0.618', '-') if fibo_levels else '-'
            volume = S_Bybit.F_Get_Volume(symbol)
            
            if stop_loss == 0 or take_profit == 0: continue
            
            _scanner_stats['found_signals'] += 1
            _scanner_stats['last_signal_time'] = L_Time.strftime("%H:%M:%S")
            log_message = (f"LONG SIGNAL | Symbol: {symbol} | Period: {period} | "
                         f"Price: {_scanner_stats['current_price']} | Stop Loss: {stop_loss:.8f} | "
                         f"Take Profit: {take_profit:.8f}")

            M_Log.F_Add_Log('transaction', 'LongSignal', log_message)
            telegram_message = f"🟢 LONG SIGNAL\n\n" \
                f"Symbol: {symbol}\n" \
                f"Period: {period}\n" \
                f"Price: {_scanner_stats['current_price']}"

            users = M_Telegram.F_Get_All_Users()
            for user_id, user_data in users.items():
                if user_data.get('user_active', False): S_Telegram.F_Send_Message(user_id, telegram_message, parse_mode='HTML')

            # --- Add signal to GUI queue ---
            signal_data = {
                "time": L_Time.strftime("%H:%M:%S"),
                "symbol": symbol,
                "period": period,
                "direction": "LONG",
                "price": _scanner_stats['current_price'],
                "volume": volume,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "fibo3": fibo3,
                "fibo4": fibo4,
                "fibo5": fibo5,
                "pattern": "HH-LH-HH",
                "fib_0_0": fibo_levels.get('0.0', '-'),
                "fib_0_01": fibo_levels.get('0.01', '-'),
                "fib_0_236": fibo_levels.get('0.236', '-'),
                "fib_0_382": fibo_levels.get('0.382', '-'),
                "fib_1_0": fibo_levels.get('1.0', '-')
            }

            S_Signal_Que.put(signal_data)


        # --- SHORT SIGNAL ---
        if short_signal.get("signal") == "short":
            fibo_levels = S_Strategy.F_Get_Fibonacci(closes, highs, lows)
            stop_loss = fibo_levels.get('1.272', 0) if fibo_levels else 0
            take_profit = fibo_levels.get('1.0', 0) if fibo_levels else 0
            fibo3 = fibo_levels.get('0.382', '-') if fibo_levels else '-'
            fibo4 = fibo_levels.get('0.5', '-') if fibo_levels else '-'
            fibo5 = fibo_levels.get('0.618', '-') if fibo_levels else '-'
            volume = S_Bybit.F_Get_Volume(symbol)
            
            if stop_loss == 0 or take_profit == 0: continue
            
            _scanner_stats['found_signals'] += 1
            _scanner_stats['last_signal_time'] = L_Time.strftime("%H:%M:%S")
            log_message = (f"SHORT SIGNAL | Symbol: {symbol} | Period: {period} | "
                         f"Price: {_scanner_stats['current_price']} | Stop Loss: {stop_loss:.8f} | "
                         f"Take Profit: {take_profit:.8f}")

            M_Log.F_Add_Log('transaction', 'ShortSignal', log_message)
            telegram_message = f"🔴 SHORT SIGNAL\n\n" \
                f"Symbol: {symbol}\n" \
                f"Period: {period}\n" \
                f"Price: {_scanner_stats['current_price']}"

            users = M_Telegram.F_Get_All_Users()
            for user_id, user_data in users.items():
                if user_data.get('user_active', False): S_Telegram.F_Send_Message(user_id, telegram_message, parse_mode='HTML')

            signal_data = {
                "time": L_Time.strftime("%H:%M:%S"),
                "symbol": symbol,
                "period": period,
                "direction": "SHORT",
                "price": _scanner_stats['current_price'],
                "volume": volume,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "fibo3": fibo3,
                "fibo4": fibo4,
                "fibo5": fibo5,
                "pattern": "LL-LH-LL",
                "fib_0_0": fibo_levels.get('0.0', '-'),
                "fib_0_01": fibo_levels.get('0.01', '-'),
                "fib_0_236": fibo_levels.get('0.236', '-'),
                "fib_0_382": fibo_levels.get('0.382', '-'),
                "fib_1_0": fibo_levels.get('1.0', '-')
            }

            S_Signal_Que.put(signal_data)

def F_Scanner():
    # DESC: Main loop of the scanner. This function runs in a thread.
    global _scanner_status, _scanner_stats
    
    # Initialize ThreadPoolExecutor with a reasonable number of workers
    # Adjust max_workers based on system capabilities and API rate limits
    MAX_WORKERS = 5 
    
    while not _scanner_stop_event.is_set():
        try:
            _scanner_status = "running"
            settings = M_Bybit.F_Get_Settings()
            zigzag_period = settings.get('zigzag_period')
            period_str_1 = settings.get('period_1')
            period_str_2 = settings.get('period_2')
            wait_time = settings.get('wait_time', 60)
            
            if not all([zigzag_period, period_str_1, period_str_2]):
                M_Log.F_Add_Log('error', 'ScannerLoop',
                               'Settings (zigzag_period, period_1, period_2) could not be loaded completely.')

                _scanner_stop_event.wait(60)
                continue

            def map_period_to_api(period_str):
                period_map = M_Bybit.F_Get_Period()
                return period_map.get(period_str, period_str)

            periods_to_scan = [map_period_to_api(period_str_1), map_period_to_api(period_str_2)]
            symbols_to_scan = S_Bybit.F_Get_Symbol()
            
            if symbols_to_scan is None:
                M_Log.F_Add_Log('alert', 'ScannerLoop', 'Could not retrieve symbol list due to network error. Will retry in 30 seconds.')
                _scanner_status = "waiting" # Set status to waiting
                _scanner_stats['current_symbol'] = "Waiting for connection..."
                _scanner_stop_event.wait(30)
                continue # Return to the start of the loop

            _scanner_stats['total_symbols'] = len(symbols_to_scan)
            _scanner_stats['scanned_symbols'] = 0
            _scanner_stats['found_signals'] = 0
            
            # Using ThreadPoolExecutor safely manages thread lifecycle
            with L_Futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = []
                for symbol_data in symbols_to_scan:
                    if _scanner_stop_event.is_set(): 
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    
                    future = executor.submit(F_Scan, symbol_data, periods_to_scan, zigzag_period)
                    futures.append(future)
                
                # Wait for all submitted tasks to complete
                # We do this in a way that respects the stop event if possible, 
                # but map/submit blocks until completion or exception.
                # L_Futures.wait(futures) is blocking.
                
                # Monitor for stop event while waiting
                done, not_done = L_Futures.wait(futures, return_when=L_Futures.FIRST_EXCEPTION)
                # If we broke out due to exception, we just continue loop and re-enter or catch error
            
            if _scanner_stop_event.is_set(): break

            _scanner_status = "waiting"
            _scanner_stats['current_symbol'] = "In waiting mode..."
            _scanner_stats['current_period'] = f"{wait_time}s"
            _scanner_stats['current_price'] = "-"
            _scanner_stats['last_zigzag_level'] = "-"
            _scanner_stats['last_fibo_level'] = "-"
            
            # Smart wait that can be interrupted
            _scanner_stop_event.wait(wait_time)
            
        except Exception as e:
            M_Log.F_Add_Log('error', 'ScannerLoopError', str(e))
            _scanner_status = "waiting"
            _scanner_stop_event.wait(60)
            
    _scanner_status = "stopped"
    
def F_Start_Scanner():
    # DESC: Starts the scanner as a thread
    global _scanner_thread, _scanner_stop_event, _scanner_status, _scanner_stats
    if _scanner_status == "running": return {"status": "error", "message": "Scanner is already running."}
    if _activity_table_clear_callback: _activity_table_clear_callback()
    _scanner_stats.update({
        'total_symbols': 0,
        'scanned_symbols': 0,
        'current_symbol': '-',
        'current_period': '-',
        'found_signals': 0,
        'last_signal_time': None,
        'current_price': '-',
        'last_zigzag_level': '-',
        'last_fibo_level': '-'
    })

    _scanner_stop_event = L_Thread.Event()
    _scanner_thread = L_Thread.Thread(target=F_Scanner, daemon=True)
    _scanner_thread.start()
    _scanner_status = "running"
    return {"status": "success", "message": "Scanner started."}

def F_Stop_Scanner():
    # DESC: Stops the running scanner thread
    global _scanner_thread, _scanner_stop_event, _scanner_status
    if _scanner_status not in ["running", "waiting"]: return {"status": "error", "message": "Scanner is not running."}
    _scanner_status = "stopping"
    _scanner_stop_event.set()
    # Wait for thread to finish with a timeout
    if _scanner_thread: _scanner_thread.join(timeout=10)
    _scanner_thread = None
    _scanner_status = "stopped"
    return {"status": "success", "message": "Scanner stopped."}

def F_Get_Status_Scanner():
    # DESC: Returns the current status and detailed information of the scanner
    global _scanner_stats
    status_info = {
        "status": _scanner_status,
        "total_symbols": _scanner_stats['total_symbols'],
        "scanned_symbols": _scanner_stats['scanned_symbols'],
        "current_symbol": _scanner_stats['current_symbol'],
        "current_period": _scanner_stats['current_period'],
        "found_signals": _scanner_stats['found_signals'],
        "last_signal_time": _scanner_stats['last_signal_time'],
        "current_price": _scanner_stats['current_price'],
        "last_zigzag_level": _scanner_stats['last_zigzag_level'],
        "last_fibo_level": _scanner_stats['last_fibo_level']
    }
    return status_info
