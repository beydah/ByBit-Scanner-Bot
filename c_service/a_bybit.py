# ----- LIBRARY --------------------------------------------------

import requests as L_Requests
import time as L_Time
from typing import Dict, List, Optional, Any, Union

from d_model import b_bybit as M_Bybit
from d_model import f_log as M_Log

# ----- FUNCTION --------------------------------------------------

def F_Get_Bybit_Symbol_Info() -> List[Dict[str, Any]]:
    # DESC: Fetches symbol information from Bybit's public API. 
    while True:
        try:
            url_info = "https://api.bybit.com/v5/market/instruments-info?category=linear"
            response_info = L_Requests.get(url_info, timeout=30)
            response_info.raise_for_status()
            data_info = response_info.json()
            return data_info.get('result', {}).get('list', [])
        except L_Requests.exceptions.RequestException as e:
            M_Log.F_Add_Log('alert', 'F_Get_Bybit_Symbol_Info', f"Network error: {e}")
            L_Time.sleep(30)
            continue
        except Exception as e:
            M_Log.F_Add_Log('error', 'F_Get_Bybit_Symbol_Info', str(e))
            return []

def F_Get_Bybit_Ticker_Info() -> List[Dict[str, Any]]:
    # DESC: Fetches ticker information from Bybit's public API. 
    while True:
        try:
            url_ticker = "https://api.bybit.com/v5/market/tickers?category=linear"
            response_ticker = L_Requests.get(url_ticker, timeout=30)
            response_ticker.raise_for_status()
            data_ticker = response_ticker.json()
            return data_ticker.get('result', {}).get('list', [])
        except L_Requests.exceptions.RequestException as e:
            M_Log.F_Add_Log('alert', 'F_Get_Bybit_Ticker_Info', f"Network error: {e}")
            L_Time.sleep(30)
            continue
        except Exception as e:
            M_Log.F_Add_Log('error', 'F_Get_Bybit_Ticker_Info', str(e))
            return []

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
    while True:
        try:
            url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={p_symbol}&interval={p_period}&limit=500"
            response = L_Requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            kline_list = data.get('result', {}).get('list', [])
            closes = [float(item[4]) for item in kline_list]
            return closes
        except L_Requests.exceptions.RequestException as e:
            M_Log.F_Add_Log('alert', 'F_Get_Close', f"Network error ({p_symbol}): {e}")
            L_Time.sleep(30)
            continue
        except Exception as e:
            M_Log.F_Add_Log('error', 'F_Get_Close', str(e))
            return []

def F_Get_High(p_symbol: str, p_period: str) -> List[float]:
    # DESC: Returns high prices for a symbol/period from Bybit.
    while True:
        try:
            url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={p_symbol}&interval={p_period}&limit=500"
            response = L_Requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            kline_list = data.get('result', {}).get('list', [])
            highs = [float(item[2]) for item in kline_list]
            return highs
        except L_Requests.exceptions.RequestException as e:
            M_Log.F_Add_Log('alert', 'F_Get_High', f"Network error ({p_symbol}): {e}")
            L_Time.sleep(30)
            continue
        except Exception as e:
            M_Log.F_Add_Log('error', 'F_Get_High', str(e))
            return []

def F_Get_Low(p_symbol: str, p_period: str) -> List[float]:
    # DESC: Returns low prices for a symbol/period from Bybit. 
    while True:
        try:
            url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={p_symbol}&interval={p_period}&limit=500"
            response = L_Requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            kline_list = data.get('result', {}).get('list', [])
            lows = [float(item[3]) for item in kline_list]
            return lows
        except L_Requests.exceptions.RequestException as e:
            M_Log.F_Add_Log('alert', 'F_Get_Low', f"Network error ({p_symbol}): {e}")
            L_Time.sleep(30)
            continue
        except Exception as e:
            M_Log.F_Add_Log('error', 'F_Get_Low', str(e))
            return []

def F_Get_Volume(p_symbol: str) -> float:
    # DESC: Returns 24h trading volume for a symbol from Bybit. p_symbol: Trading pair (e.g., 'BTCUSDT').
    try:
        url = "https://api.bybit.com/v5/market/tickers?category=linear"
        response = L_Requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        tickers = data.get('result', {}).get('list', [])
        for ticker in tickers:
            if ticker.get('symbol') == p_symbol: return float(ticker.get('turnover24h', 0))
            
        return 0.0
    except L_Requests.exceptions.RequestException as e:
        M_Log.F_Add_Log('alert', 'F_Get_Volume', f"Network error ({p_symbol}): {e}")
        return 0.0
    except Exception as e:
        M_Log.F_Add_Log('error', 'F_Get_Volume', str(e))
        return 0.0
