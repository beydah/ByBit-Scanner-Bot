# ----- HEADER --------------------------------------------------

# File: signal_logic.py
# Description: Auto-generated header for structural compliance.

# ----- FUNCTION --------------------------------------------------

def F_Get_Highest(p_high, p_period):
    # DESC: Implements logic similar to TradingView's ta.highestbars function
    if len(p_high) < p_period: return None
    recent_highs = p_high[-p_period:]
    max_index = recent_highs.index(max(recent_highs))
    return len(p_high) - p_period + max_index

def F_Get_Lowest(p_low, p_period):
    # DESC: Implements logic similar to TradingView's ta.lowestbars function
    if len(p_low) < p_period: return None
    recent_lows = p_low[-p_period:]
    min_index = recent_lows.index(min(recent_lows))
    return len(p_low) - p_period + min_index

def F_Get_ZigZag(p_close, p_high, p_low, p_period):
    # DESC: Generates zigzag data points similar to TradingView's zigzag indicator
    if len(p_close) < p_period * 2: return []
    zigzag_points = []
    for i in range(p_period, len(p_close) - p_period):
        is_high = True
        for j in range(i - p_period, i + p_period + 1):
            if j != i and p_high[j] >= p_high[i]:
                is_high = False
                break
        
        is_low = True
        for j in range(i - p_period, i + p_period + 1):
            if j != i and p_low[j] <= p_low[i]:
                is_low = False
                break
        
        if is_high:
            if len(zigzag_points) > 0:
                prev_highs = []
                for point in zigzag_points:
                    if point[2] in ['HH', 'HL']: prev_highs.append(point[1])
                
                if prev_highs:
                    max_prev_high = max(prev_highs)
                    if p_high[i] > max_prev_high: label = 'HH'  # Higher High
                    else: label = 'LH'  # Lower High
                else: label = 'HH'  # First high point
            else: label = 'HH'  # First point
            zigzag_points.append([i, p_high[i], label])
        
        elif is_low:
            if len(zigzag_points) > 0:
                prev_lows = []
                for point in zigzag_points:
                    if point[2] in ['LL', 'LH']: prev_lows.append(point[1])
                
                if prev_lows:
                    min_prev_low = min(prev_lows)
                    if p_low[i] < min_prev_low: label = 'LL'  # Lower Low
                    else: label = 'HL'  # Higher Low
                else: label = 'LL'  # First low point
            else: label = 'LL'  # First point
            zigzag_points.append([i, p_low[i], label])
    return zigzag_points

def F_Calculate_Fib_Levels_Long(p_b_point, p_x_point):
    # DESC: Calculates Fibonacci retracement levels for long positions between X (bottom) and B (last HH). 0 level at B, 1 at X.
    diff = p_b_point - p_x_point
    if diff <= 0: return {}
    levels = {
        '0.0': p_b_point,
        '0.01': p_b_point - diff * 0.01,
        '0.236': p_b_point - diff * 0.236,
        '0.382': p_b_point - diff * 0.382,
        '0.5': p_b_point - diff * 0.5,
        '0.618': p_b_point - diff * 0.618,
        '0.786': p_b_point - diff * 0.786,
        '1.0': p_x_point,
        '1.272': p_x_point - diff * 0.272  # Stop Loss
    }
    return levels

def F_Calculate_Fib_Levels_Short(p_b_point, p_x_point):
    # DESC: Calculates Fibonacci retracement levels for short positions between X (top) and B (last LL). 0 level at B, 1 at X.
    diff = p_x_point - p_b_point
    if diff <= 0: return {}
    levels = {
        '0.0': p_b_point,
        '0.01': p_b_point + diff * 0.01,
        '0.236': p_b_point + diff * 0.236,
        '0.382': p_b_point + diff * 0.382,
        '0.5': p_b_point + diff * 0.5,
        '0.618': p_b_point + diff * 0.618,
        '0.786': p_b_point + diff * 0.786,
        '1.0': p_x_point
    }
    return levels

def F_Get_Long_Signal(p_close, p_high, p_low, p_zigzag_period):
    # DESC: Finds HH(a)-LH(x)-HH(b) pattern in ZigZag series, calculates AxB Fibonacci levels, and performs chain validation
    zigzag_points = F_Get_ZigZag(p_close, p_high, p_low, p_zigzag_period)
    if len(zigzag_points) < 3: return {"signal": "none", "reason": "Not enough ZigZag points"}
    for i in range(len(zigzag_points) - 2):
        label_a, label_x, label_b = zigzag_points[i][2], zigzag_points[i+1][2], zigzag_points[i+2][2]
        if label_a == 'HH' and label_x == 'LH' and label_b == 'HH':
            a_idx, a_price = zigzag_points[i][0], zigzag_points[i][1]
            x_idx, x_price = zigzag_points[i+1][0], zigzag_points[i+1][1]
            b_idx, b_price = zigzag_points[i+2][0], zigzag_points[i+2][1]
            if abs(b_price - x_price) / x_price < 0.02: continue
            fib = F_Calculate_Fib_Levels_Long(b_price, x_price)
            if (fib['1.0'] != x_price) or (fib['0.0'] != b_price): continue
            chain = [
                ('0.382', '0.01'),
                ('0.5', '0.236'),
                ('0.618', '0.382'),
                ('0.786', '0.618'),
                ('1.0', None)
            ]

            right = b_idx
            left = a_idx
            for step, (must_touch, must_not_touch) in enumerate(chain):
                found = False
                touch_idx = None
                for j in range(right, left-1, -1):
                    values = [p_high[j], p_low[j], p_close[j]]
                    touched = min(values) <= fib[must_touch] <= max(values)
                    not_touched = False
                    if must_not_touch: not_touched = min(values) <= fib[must_not_touch] <= max(values)
                    if touched and not not_touched:
                        found = True
                        touch_idx = j
                        break

                if not found: return {"signal": "none", "reason": f"Chain validation failed at {must_touch}"}
                right = touch_idx - 1  # Narrow down the range for next step
            return {"signal": "long", "reason": "Long signal generated with AxB ZigZag and Fibonacci chain"}
    return {"signal": "none", "reason": "No HH-LH-HH pattern found"}

def F_Get_Short_Signal(p_close, p_high, p_low, p_zigzag_period):
    # DESC: Finds LL(a)-LH(x)-LL(b) pattern in ZigZag series, calculates AxB Fibonacci levels, and performs chain validation
    zigzag_points = F_Get_ZigZag(p_close, p_high, p_low, p_zigzag_period)
    if len(zigzag_points) < 3: return {"signal": "none", "reason": "Not enough ZigZag points"}
    for i in range(len(zigzag_points) - 2):
        label_a, label_x, label_b = zigzag_points[i][2], zigzag_points[i+1][2], zigzag_points[i+2][2]
        if label_a == 'LL' and label_x == 'LH' and label_b == 'LL':
            a_idx, a_price = zigzag_points[i][0], zigzag_points[i][1]
            x_idx, x_price = zigzag_points[i+1][0], zigzag_points[i+1][1]
            b_idx, b_price = zigzag_points[i+2][0], zigzag_points[i+2][1]
            if abs(b_price - x_price) / x_price < 0.02: continue
            fib = F_Calculate_Fib_Levels_Short(b_price, x_price)
            if (fib['1.0'] != x_price) or (fib['0.0'] != b_price): continue
            chain = [
                ('0.382', '0.01'),
                ('0.5', '0.236'),
                ('0.618', '0.382'),
                ('0.786', '0.618'),
                ('1.0', None)
            ]

            right = b_idx
            left = a_idx
            for step, (must_touch, must_not_touch) in enumerate(chain):
                found = False
                touch_idx = None
                for j in range(right, left-1, -1):
                    values = [p_high[j], p_low[j], p_close[j]]
                    touched = min(values) <= fib[must_touch] <= max(values)
                    not_touched = False
                    if must_not_touch: not_touched = min(values) <= fib[must_not_touch] <= max(values)
                    if touched and not not_touched:
                        found = True
                        touch_idx = j
                        break

                if not found: return {"signal": "none", "reason": f"Chain validation failed at {must_touch}"}
                right = touch_idx - 1
            return {"signal": "short", "reason": "Short signal generated with AxB ZigZag and Fibonacci chain"}
    return {"signal": "none", "reason": "No LL-LH-LL pattern found"}

def F_Get_Fibonacci(p_close, p_high, p_low):
    # DESC: Returns appropriate Fibonacci levels based on the last two ZigZag points. Calculates for long if last ZigZag is HH, for short if LL.
    zigzag_points = F_Get_ZigZag(p_close, p_high, p_low, 10)  # Default period 10, can be parameterized if needed
    if len(zigzag_points) < 2: return {}
    _, last_price, last_label = zigzag_points[-1]
    _, prev_price, _ = zigzag_points[-2]
    if last_label == 'HH': return F_Calculate_Fib_Levels_Long(last_price, prev_price)
    elif last_label == 'LL': return F_Calculate_Fib_Levels_Short(last_price, prev_price)
    else: return {}
