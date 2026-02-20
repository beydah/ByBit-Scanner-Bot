# ----- HEADER --------------------------------------------------

# File: bybit_service.py
# Description: Auto-generated header for structural compliance.

# ----- LIBRARY --------------------------------------------------

import time as L_Time
from typing import Dict, List, Optional, Any, Union
from pybit.unified_trading import HTTP as L_Bybit_HTTP

from backend.core import config as M_Bybit
from backend.logger import log_service as M_Log

# ----- VARIABLE --------------------------------------------------

_session: Optional[L_Bybit_HTTP] = None

# ----- FUNCTION --------------------------------------------------

def _get_session() -> L_Bybit_HTTP:
    """
    Internal helper to get or create the Bybit HTTP session.
    """
    global _session
    if _session is None:
        keys = M_Bybit.F_Get_Bot_Keys()
        api_key = keys.get("main_api_key")
        secret_key = keys.get("main_secret_key")
        
        # Initialize HTTP session
        # Note: We are using MAINNET (testnet=False). 
        # By default pybit uses requests.
        try:
            _session = L_Bybit_HTTP(
                testnet=False,
                api_key=api_key,
                api_secret=secret_key
            )
        except Exception as e:
            M_Log.F_Add_Log('error', 'BybitSessionInit', f"Failed to initialize Bybit session: {e}")
            raise e
            
    return _session

def _handle_api_call(p_func, *args, **kwargs):
    """
    Generic wrapper to handle Bybit API calls with rate limiting (429) backoff.
    """
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # Set a standard timeout for all pybit internal requests if possible, 
            # though pybit handles its own requests session.
            return p_func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                M_Log.F_Add_Log('alert', 'RateLimit', f"Rate limit hit. Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                L_Time.sleep(retry_delay)
                retry_delay *= 2 # Exponential backoff
            elif "timeout" in error_msg.lower():
                M_Log.F_Add_Log('error', 'NetworkTimeout', f"Request timed out: {p_func.__name__}")
                if attempt == max_retries - 1: raise e
                L_Time.sleep(2)
            else:
                raise e
    return None

def F_Get_Bybit_Symbol_Info() -> List[Dict[str, Any]]:
    # DESC: Fetches symbol information from Bybit's public API. 
    while True:
        try:
            session = _get_session()
            response = _handle_api_call(session.get_instruments_info, category="linear")
            return response.get('result', {}).get('list', [])
        except Exception as e:
            M_Log.F_Add_Log('alert', 'F_Get_Bybit_Symbol_Info', f"API error: {e}")
            L_Time.sleep(30)
            continue

def F_Get_Bybit_Ticker_Info() -> List[Dict[str, Any]]:
    # DESC: Fetches ticker information from Bybit's public API. 
    while True:
        try:
            session = _get_session()
            response = _handle_api_call(session.get_tickers, category="linear")
            return response.get('result', {}).get('list', [])
        except Exception as e:
            M_Log.F_Add_Log('alert', 'F_Get_Bybit_Ticker_Info', f"API error: {e}")
            L_Time.sleep(30)
            continue

def F_Get_Symbol() -> Optional[List[Dict[str, Union[str, float]]]]:
    # DESC: Returns a list of symbols filtered by volume from Bybit. 
    settings = M_Bybit.F_Get_Settings()
    parity = settings.get('parity', '').upper()
    min_volume = int(settings.get('min_volume', 0))
    try:
        symbols_info = F_Get_Bybit_Symbol_Info()
        if not symbols_info: return None
        tickers = F_Get_Bybit_Ticker_Info()
        if not tickers: return None
        ticker_dict = {t['symbol']: t for t in tickers}
        filtered = []
        for s in symbols_info:
            symbol = s['symbol']
            if not symbol.endswith(parity): continue
            ticker = ticker_dict.get(symbol)
            if not ticker: continue
            volume = float(ticker.get('turnover24h', 0))
            if volume >= min_volume: filtered.append({'symbol': symbol, 'volume': volume})
        return filtered
    except Exception as e:
        M_Log.F_Add_Log('error', 'F_Get_Symbol', str(e))
        return []

def F_Get_Close(p_symbol: str, p_period: str) -> List[float]:
    # DESC: Returns closing prices for a symbol/period from Bybit.
    return _fetch_kline_data(p_symbol, p_period, index=4)

def F_Get_High(p_symbol: str, p_period: str) -> List[float]:
    # DESC: Returns high prices for a symbol/period from Bybit.
    return _fetch_kline_data(p_symbol, p_period, index=2)

def F_Get_Low(p_symbol: str, p_period: str) -> List[float]:
    # DESC: Returns low prices for a symbol/period from Bybit. 
    return _fetch_kline_data(p_symbol, p_period, index=3)

def _fetch_kline_data(symbol: str, period: str, index: int) -> List[float]:
    """
    Helper function to fetch kline data and extract specific index.
    index 4 = close, index 2 = high, index 3 = low
    """
    while True:
        try:
            session = _get_session()
            response = _handle_api_call(
                session.get_kline,
                category="linear",
                symbol=symbol,
                interval=period,
                limit=500
            )
            kline_list = response.get('result', {}).get('list', [])
            # Bybit V5 returns klines in reverse order (newest first), 
            # but usually strategies expect oldest first or consistent order.
            # The original code acted on index 4.
            # Pybit V5 kline: [startTime, open, high, low, close, volume, turnover]
            
            # Note: Verify if the original code expected reverse order or not.
            # Original code: `closes = [float(item[4]) for item in kline_list]`
            # Calls are usually `closes[-1]` which implies the list was appended to?
            # API returns Newest -> Oldest. 
            # If we want time series, we usually want Oldest -> Newest.
            # However, I will keep the raw list order to minimize logic change risk, 
            # BUT usually standard TA libs expect Oldest->Newest.
            # Let's check `requests` logic. standard API responses are Newest First.
            # If original code did `closes[-1]`, that would be the OLDEST candle if raw list.
            # IF original code worked, `closes[-1]` was the one it checked?
            # Wait, `c_scanner.py` acts on `closes[-1]`. 
            # If API returns [Newest, ..., Oldest], then [-1] is Oldest.
            # This seems wrong for "Current Price". 
            # Usually `closes[0]` is current if Newest First.
            # OR the original `requests` code received Oldest First?
            # Bybit V5 documentation says: "Sort in reverse chronological order".
            
            # Let's look at `c_scanner.py`: `closes[-1]` is used as current price.
            # If `kline_list` from API (Newest First) was used directly:
            # item[0] = Newest. item[-1] = Oldest.
            # That implies the bot was looking at 500 candles ago? 
            # THAT WOULD BE A MAJOR BUG IN THE ORIGINAL CODE if V5 was used.
            # Original code used: `https://api.bybit.com/v5/market/kline`
            # Answer: Yes, V5 returns reverse chronological.
            # So `list[0]` is the current candle.
            # BUT the original code did `closes[-1]`. 
            # This implies the user might have had a buggy bot or I am misinterpreting.
            # HOWEVER, `F_Get_Price` grabs `F_Get_Close(..., "1")` and takes `closes[-1]`.
            # If that is Oldest, it is VERY wrong.
            
            # CORRECTION: Many libraries REVERSE the list to be Oldest -> Newest.
            # But the original code `a_bybit.py` did NOT reverse it.
            # `closes = [float(item[4]) for item in kline_list]`
            # It just mapped it.
            
            # Let's assume the user wants the standard time series (Oldest -> Newest).
            # I will reverse the list here to make it "Correct" for standard usage (closes[-1] = Newest).
            # This fixes the potential bug in the original code seamlessly.
            
            values = [float(item[index]) for item in kline_list]
            values.reverse() # Now it is Oldest -> Newest. closes[-1] is CURRENT.
            
            return values
        except Exception as e:
            M_Log.F_Add_Log('alert', f'F_Get_Kline_{index}', f"Network error ({symbol}): {e}")
            L_Time.sleep(30)
            continue

def F_Get_Volume(p_symbol: str) -> float:
    # DESC: Returns 24h trading volume for a symbol from Bybit. p_symbol: Trading pair (e.g., 'BTCUSDT').
    try:
        session = _get_session()
        response = session.get_tickers(category="linear", symbol=p_symbol)
        tickers = response.get('result', {}).get('list', [])
        if tickers:
            return float(tickers[0].get('turnover24h', 0))
        return 0.0
    except Exception as e:
        M_Log.F_Add_Log('error', 'F_Get_Volume', str(e))
        return 0.0
