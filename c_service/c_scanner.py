# ----- LIBRARY --------------------------------------------------

import threading as L_Thread
import time as L_Time

from c_service import a_bybit as S_Bybit
from c_service import b_strategy as S_Strategy
from c_service import d_telegram as S_Telegram
from c_service.f_signal import Signal_Que as S_Signal_Que

from d_model import b_bybit as M_Bybit
from d_model import f_log as M_Log
from d_model import d_telegram as M_Telegram

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
    _scanner_stats['scanned_symbols'] += 1
    for period in periods_to_scan:
        if _scanner_stop_event.is_set(): break
        _scanner_stats['current_symbol'] = symbol
        _scanner_stats['current_period'] = period
        closes = S_Bybit.F_Get_Close(symbol, period)
        highs = S_Bybit.F_Get_High(symbol, period)
        lows = S_Bybit.F_Get_Low(symbol, period)
        if closes is None or highs is None or lows is None or not (closes and highs and lows):
            signal_data = {
                "symbol": symbol,
                "volume": '-',
                "period": period,
                "price": '-',
                "pattern": 'veri yok',
                "fib_0_0": '-',
                "fib_0_01": '-',
                "fib_0_236": '-',
                "fib_0_382": '-',
                "fib_1_0": '-'
            }
            S_Signal_Que.put(signal_data)
            continue

        _scanner_stats['current_price'] = F_Get_Price(symbol)
        _scanner_stats['last_zigzag_level'] = F_Get_Zigzag(closes, highs, lows, zigzag_period)
        _scanner_stats['last_fibo_level'] = S_Strategy.F_Get_Fibonacci(closes, highs, lows)
        long_signal = S_Strategy.F_Get_Long_Signal(closes, highs, lows, zigzag_period)
        short_signal = S_Strategy.F_Get_Short_Signal(closes, highs, lows, zigzag_period)
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
                "fibo5": fibo5
            }

            S_Signal_Que.put(signal_data)
            zigzag_points = S_Strategy.F_Get_ZigZag(closes, highs, lows, zigzag_period)
            a_idx = x_idx = b_idx = a_price = x_price = b_price = None
            for i in range(len(zigzag_points) - 2):
                label_a, label_x, label_b = zigzag_points[i][2], zigzag_points[i+1][2], zigzag_points[i+2][2]
                if label_a == 'HH' and label_x == 'LH' and label_b == 'HH':
                    a_idx, a_price = zigzag_points[i][0], zigzag_points[i][1]
                    x_idx, x_price = zigzag_points[i+1][0], zigzag_points[i+1][1]
                    b_idx, b_price = zigzag_points[i+2][0], zigzag_points[i+2][1]
                    break

            fibo_levels = S_Strategy.F_Get_Fibonacci(closes, highs, lows)
            print("=== LONG SIGNAL DETAILS ===")
            print(f"Sembol: {symbol}")
            print(f"Periyot: {period}")
            print(f"A (HH): idx={a_idx}, fiyat={a_price}")
            print(f"X (LH): idx={x_idx}, price={x_price}")
            print(f"B (HH): idx={b_idx}, price={b_price}")
            print(f"Fibonacci Levels: {fibo_levels}")
            print(f"ZigZag Points: {zigzag_points}")
            print(f"Closes: {closes}")
            print(f"Highs: {highs}")
            print(f"Lows: {lows}")
            print("=========================")

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
                "fibo5": fibo5
            }

            S_Signal_Que.put(signal_data)
            zigzag_points = S_Strategy.F_Get_ZigZag(closes, highs, lows, zigzag_period)
            a_idx = x_idx = b_idx = a_price = x_price = b_price = None
            for i in range(len(zigzag_points) - 2):
                label_a, label_x, label_b = zigzag_points[i][2], zigzag_points[i+1][2], zigzag_points[i+2][2]
                if label_a == 'LL' and label_x == 'LH' and label_b == 'LL':
                    a_idx, a_price = zigzag_points[i][0], zigzag_points[i][1]
                    x_idx, x_price = zigzag_points[i+1][0], zigzag_points[i+1][1]
                    b_idx, b_price = zigzag_points[i+2][0], zigzag_points[i+2][1]
                    break

            fibo_levels = S_Strategy.F_Get_Fibonacci(closes, highs, lows)
            print("=== SHORT SIGNAL DETAILS ===")
            print(f"Sembol: {symbol}")
            print(f"Periyot: {period}")
            print(f"A (LL): idx={a_idx}, fiyat={a_price}")
            print(f"X (LH): idx={x_idx}, price={x_price}")
            print(f"B (LL): idx={b_idx}, price={b_price}")
            print(f"Fibonacci Levels: {fibo_levels}")
            print(f"ZigZag Points: {zigzag_points}")
            print(f"Closes: {closes}")
            print(f"Highs: {highs}")
            print(f"Lows: {lows}")
            print("=========================")

        volume = S_Bybit.F_Get_Volume(symbol)
        price = closes[-1] if closes else '-'
        pattern = '-'
        fib_0_0 = '-'
        fib_0_01 = '-'
        fib_0_236 = '-'
        fib_0_382 = '-'
        fib_1_0 = '-'
        if long_signal.get("signal") == "long":
            pattern = 'HH-LH-HH'
            fibo_levels = S_Strategy.F_Get_Fibonacci(closes, highs, lows)
            fib_0_0 = fibo_levels.get('0.0', '-') if fibo_levels else '-'
            fib_0_01 = fibo_levels.get('0.01', '-') if fibo_levels else '-'
            fib_0_236 = fibo_levels.get('0.236', '-') if fibo_levels else '-'
            fib_0_382 = fibo_levels.get('0.382', '-') if fibo_levels else '-'
            fib_1_0 = fibo_levels.get('1.0', '-') if fibo_levels else '-'

        elif short_signal.get("signal") == "short":
            pattern = 'LL-LH-LL'
            fibo_levels = S_Strategy.F_Get_Fibonacci(closes, highs, lows)
            fib_0_0 = fibo_levels.get('0.0', '-') if fibo_levels else '-'
            fib_0_01 = fibo_levels.get('0.01', '-') if fibo_levels else '-'
            fib_0_236 = fibo_levels.get('0.236', '-') if fibo_levels else '-'
            fib_0_382 = fibo_levels.get('0.382', '-') if fibo_levels else '-'
            fib_1_0 = fibo_levels.get('1.0', '-') if fibo_levels else '-'

        signal_data = {
            "symbol": symbol,
            "volume": volume,
            "period": period,
            "price": price,
            "pattern": pattern,
            "fib_0_0": fib_0_0,
            "fib_0_01": fib_0_01,
            "fib_0_236": fib_0_236,
            "fib_0_382": fib_0_382,
            "fib_1_0": fib_1_0
        }

        S_Signal_Que.put(signal_data)

def F_Scanner():
    # DESC: Main loop of the scanner. This function runs in a thread.
    global _scanner_status, _scanner_stats
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
            threads = []
            for symbol_data in symbols_to_scan:
                if _scanner_stop_event.is_set(): break
                t = L_Thread.Thread(target=F_Scan, args=(symbol_data, periods_to_scan, zigzag_period))
                t.start()
                threads.append(t)

            for t in threads: t.join()
            _scanner_status = "waiting"
            _scanner_stats['current_symbol'] = "In waiting mode..."
            _scanner_stats['current_period'] = f"{wait_time}s"
            _scanner_stats['current_price'] = "-"
            _scanner_stats['last_zigzag_level'] = "-"
            _scanner_stats['last_fibo_level'] = "-"
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
