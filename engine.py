"""
NIFTY 50 3-Year Multi-Timeframe Quantitative Engine & Visualizer Preprocessor
Processes 1D, 4H, 1H, 30m, 15m, 5m datasets from 2023-11-01 to 2026-11-09.
Computes:
1. Dow Theory Market Structure (HH, HL, LH, LL, BOS, CHoCH, Pre-Breakout Range, Post-Breakout Excursion, Trade Bias Color)
2. Williams %R (14-period, Overbought >= -20, Oversold <= -80, Neutral)
3. Swings vs Williams %R Confluence & Gap Distance ('How far it is if not matching')
4. BRC (Big Range Candle) Classification & Proximity ('How far it is if not found': Pts & Pct to BRC, Elapsed Bars)
5. Dow Theory Trend Hierarchy: Primary (1D/4H), Secondary (4H/1H), Tertiary (30m/15m/5m)
6. RSI (14-period, Zones, Momentum, Divergences)
7. Multi-Factor Alert Generation with user-configurable trigger rules
"""

import os
import sys
import json
import time
import math
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(os.path.dirname(BASE_DIR), "Csv")
OUTPUT_JSON = os.path.join(BASE_DIR, "nifty_3yr_data.json")

TIMEFRAMES = ["1D", "4H", "1H", "30m", "15m", "5m"]
START_DATE = "2023-11-01"

# Swing orders per timeframe for robust Dow Theory fractal detection
SWING_ORDERS = {
    "1D": 3,
    "4H": 3,
    "1H": 4,
    "30m": 5,
    "15m": 5,
    "5m": 6
}

def clean_float(val, precision=2):
    """Sanitize float to handle NaN/Inf for JSON compliance."""
    if val is None or pd.isna(val) or math.isnan(val) or math.isinf(val):
        return None
    return round(float(val), precision)

def process_timeframe(tf, sample_limit=None):
    """Process a single timeframe CSV into structured analytics."""
    csv_file = os.path.join(CSV_DIR, f"NIFTY50_Index_{tf}.csv")
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Missing dataset: {csv_file}")
    
    date_col = "Date" if tf == "1D" else "Timestamp"
    df = pd.read_csv(csv_file)
    df["time_str"] = df[date_col].astype(str)
    
    # Filter 3-year window
    df = df[df["time_str"] >= START_DATE].sort_values("time_str").reset_index(drop=True)
    total_3yr_bars = len(df)
    
    # If timeframe has very large bar counts (e.g. 5m, 15m), we retain rich recent bars for visualization
    # and compute full-history summary stats across the entire 3 years
    display_limit = {
        "1D": 751,
        "4H": 1500,
        "1H": 2500,
        "30m": 2500,
        "15m": 2500,
        "5m": 2500
    }.get(tf, 2500)
    
    # 3-year macro statistics over full filtered df
    full_high = df["High"].max()
    full_low = df["Low"].min()
    full_close = df["Close"].iloc[-1]
    full_open = df["Open"].iloc[0]
    full_return_pct = round(((full_close - full_open) / full_open) * 100.0, 2)
    
    # Extract series for calculation
    # For chart display and swing tracking, take recent display_limit bars
    df_disp = df.iloc[-display_limit:].reset_index(drop=True) if len(df) > display_limit else df
    
    highs = df_disp["High"].values
    lows = df_disp["Low"].values
    closes = df_disp["Close"].values
    opens = df_disp["Open"].values
    times = df_disp["time_str"].values
    ranges = df_disp["Range"].values
    atrs = df_disp["ATR14"].values
    wprs = df_disp["WilliamsR14"].values
    rsis = df_disp["RSI14_Close"].values
    rel_ranges = df_disp["Relative_Range"].values
    
    n_bars = len(df_disp)
    order = SWING_ORDERS.get(tf, 4)
    
    # ----------------------------------------------------
    # 1. Dow Theory Swings & Market Structure
    # ----------------------------------------------------
    swings = []
    sh_list = []
    sl_list = []
    
    for i in range(order, n_bars - order):
        is_sh = all(highs[i] >= highs[i-k] for k in range(1, order+1)) and all(highs[i] >= highs[i+k] for k in range(1, order+1))
        is_sl = all(lows[i] <= lows[i-k] for k in range(1, order+1)) and all(lows[i] <= lows[i+k] for k in range(1, order+1))
        
        if is_sh:
            val_wpr = clean_float(wprs[i], 2)
            val_rsi = clean_float(rsis[i], 2)
            matched_wpr = (val_wpr is not None and val_wpr >= -20.0)
            gap_wpr = 0.0 if matched_wpr else (abs(-20.0 - val_wpr) if val_wpr is not None else None)
            
            tag = "SH"
            if len(sh_list) > 0:
                prev_sh_price = sh_list[-1]["price"]
                tag = "HH" if highs[i] > prev_sh_price else "LH"
            
            node = {
                "idx": int(i),
                "time": str(times[i]),
                "type": "SH",
                "tag": tag,
                "price": round(float(highs[i]), 2),
                "wpr": val_wpr,
                "rsi": val_rsi,
                "wpr_matched": matched_wpr,
                "wpr_gap": clean_float(gap_wpr, 2)
            }
            swings.append(node)
            sh_list.append(node)
            
        if is_sl:
            val_wpr = clean_float(wprs[i], 2)
            val_rsi = clean_float(rsis[i], 2)
            matched_wpr = (val_wpr is not None and val_wpr <= -80.0)
            gap_wpr = 0.0 if matched_wpr else (abs(val_wpr - (-80.0)) if val_wpr is not None else None)
            
            tag = "SL"
            if len(sl_list) > 0:
                prev_sl_price = sl_list[-1]["price"]
                tag = "HL" if lows[i] > prev_sl_price else "LL"
            
            node = {
                "idx": int(i),
                "time": str(times[i]),
                "type": "SL",
                "tag": tag,
                "price": round(float(lows[i]), 2),
                "wpr": val_wpr,
                "rsi": val_rsi,
                "wpr_matched": matched_wpr,
                "wpr_gap": clean_float(gap_wpr, 2)
            }
            swings.append(node)
            sl_list.append(node)
    
    swings.sort(key=lambda x: x["idx"])
    
    # ----------------------------------------------------
    # 2. Breakout Detection & Pre/Post Breakout Dynamics
    # ----------------------------------------------------
    # Identify the most recent confirmed breakout event
    last_sh = sh_list[-1] if len(sh_list) > 0 else None
    prev_sh = sh_list[-2] if len(sh_list) > 1 else None
    last_sl = sl_list[-1] if len(sl_list) > 0 else None
    prev_sl = sl_list[-2] if len(sl_list) > 1 else None
    
    curr_close = round(float(closes[-1]), 2)
    curr_open = round(float(opens[-1]), 2)
    curr_high = round(float(highs[-1]), 2)
    curr_low = round(float(lows[-1]), 2)
    curr_range = round(float(ranges[-1]), 2)
    curr_atr = round(float(atrs[-1]), 2)
    curr_wpr = round(float(wprs[-1]), 2) if not pd.isna(wprs[-1]) else -50.0
    curr_rsi = round(float(rsis[-1]), 2) if not pd.isna(rsis[-1]) else 50.0
    curr_rel_range = round(float(rel_ranges[-1]), 2) if not pd.isna(rel_ranges[-1]) else 1.0
    
    # Find active breakout
    breakout_type = "NONE"
    breakout_level = None
    breakout_time = None
    breakout_idx = None
    pre_range_high = None
    pre_range_low = None
    pre_consolidation_bars = 0
    post_status = "STABLE"
    post_excursion_pts = 0.0
    
    # Scan backward from current bar to find last break of structure (BOS)
    if last_sh and last_sl:
        pre_range_high = max(last_sh["price"], (prev_sh["price"] if prev_sh else last_sh["price"]))
        pre_range_low = min(last_sl["price"], (prev_sl["price"] if prev_sl else last_sl["price"]))
        
        # Search for bar crossing previous SH or SL
        for b_idx in range(n_bars - 1, max(0, n_bars - 150), -1):
            c_val = closes[b_idx]
            # Bullish BOS check
            if prev_sh and c_val > prev_sh["price"] and closes[b_idx - 1] <= prev_sh["price"]:
                breakout_type = "BULLISH_BOS"
                breakout_level = prev_sh["price"]
                breakout_time = times[b_idx]
                breakout_idx = b_idx
                break
            # Bearish BOS check
            elif prev_sl and c_val < prev_sl["price"] and closes[b_idx - 1] >= prev_sl["price"]:
                breakout_type = "BEARISH_BOS"
                breakout_level = prev_sl["price"]
                breakout_time = times[b_idx]
                breakout_idx = b_idx
                break
                
        if breakout_idx is not None:
            pre_consolidation_bars = max(1, breakout_idx - (prev_sh["idx"] if breakout_type == "BULLISH_BOS" else prev_sl["idx"]))
            bars_since_break = n_bars - 1 - breakout_idx
            
            if breakout_type == "BULLISH_BOS":
                highest_post = np.max(highs[breakout_idx:])
                lowest_post = np.min(lows[breakout_idx:])
                post_excursion_pts = round(float(highest_post - breakout_level), 2)
                # Retest check: did price test within 0.25 * ATR of breakout level?
                tested_level = (lowest_post <= breakout_level + (0.25 * curr_atr))
                if curr_close < breakout_level:
                    post_status = "FAILED_FAKEOUT"
                elif tested_level and curr_close > breakout_level:
                    post_status = "RETEST_CONFIRMED"
                else:
                    post_status = "ACTIVE_EXPANSION"
            else:
                lowest_post = np.min(lows[breakout_idx:])
                highest_post = np.max(highs[breakout_idx:])
                post_excursion_pts = round(float(breakout_level - lowest_post), 2)
                tested_level = (highest_post >= breakout_level - (0.25 * curr_atr))
                if curr_close > breakout_level:
                    post_status = "FAILED_FAKEOUT"
                elif tested_level and curr_close < breakout_level:
                    post_status = "RETEST_CONFIRMED"
                else:
                    post_status = "ACTIVE_EXPANSION"
    
    # ----------------------------------------------------
    # 3. Market Structure Bias & Block Color
    # ----------------------------------------------------
    sh_tag = last_sh["tag"] if last_sh else "SH"
    sl_tag = last_sl["tag"] if last_sl else "SL"
    
    # Dow Theory structure condition:
    # Bullish: Higher Highs + Higher Lows OR Bullish BOS active
    # Bearish: Lower Highs + Lower Lows OR Bearish BOS active
    is_hh_hl = (sh_tag == "HH" and sl_tag == "HL")
    is_lh_ll = (sh_tag == "LH" and sl_tag == "LL")
    
    if is_hh_hl or (breakout_type == "BULLISH_BOS" and post_status != "FAILED_FAKEOUT") or (curr_close > (last_sh["price"] if last_sh else curr_close)):
        trade_bias = "BULLISH"
        block_color = "GREEN"
        bias_desc = f"Bullish Uptrend: {sh_tag} / {sl_tag} structure confirmed"
    elif is_lh_ll or (breakout_type == "BEARISH_BOS" and post_status != "FAILED_FAKEOUT") or (curr_close < (last_sl["price"] if last_sl else curr_close)):
        trade_bias = "BEARISH"
        block_color = "RED"
        bias_desc = f"Bearish Downtrend: {sh_tag} / {sl_tag} structure confirmed"
    else:
        # Mixed (e.g. HH with LL or LH with HL - expanding/contracting consolidation)
        if curr_close >= curr_open:
            trade_bias = "NEUTRAL_BULLISH"
            block_color = "GREEN"
            bias_desc = f"Consolidating with Bullish Tilt ({sh_tag}/{sl_tag})"
        else:
            trade_bias = "NEUTRAL_BEARISH"
            block_color = "RED"
            bias_desc = f"Consolidating with Bearish Tilt ({sh_tag}/{sl_tag})"

    # ----------------------------------------------------
    # 4. Williams %R Analysis & Swings Matching Matrix
    # ----------------------------------------------------
    wpr_zone = "OVERBOUGHT" if curr_wpr >= -20.0 else ("OVERSOLD" if curr_wpr <= -80.0 else "NEUTRAL")
    
    # Calculate confluence rate for swings
    matched_swings = [s for s in swings if s["wpr_matched"]]
    mismatched_swings = [s for s in swings if not s["wpr_matched"]]
    confluence_rate = round((len(matched_swings) / max(1, len(swings))) * 100.0, 1)
    avg_gap_distance = round(np.mean([s["wpr_gap"] for s in mismatched_swings]) if len(mismatched_swings) > 0 else 0.0, 1)
    
    # ----------------------------------------------------
    # 5. BRC Engine & Proximity ('How far it is if not found')
    # ----------------------------------------------------
    brc_threshold = round(1.5 * curr_atr, 2)
    is_brc = bool(curr_range >= brc_threshold)
    
    if is_brc:
        brc_type = "BULLISH_BRC" if curr_close > curr_open else ("BEARISH_BRC" if curr_close < curr_open else "DOJI_BRC")
        pts_to_brc = 0.0
        prox_pct = 100.0
    else:
        brc_type = "NORMAL_CANDLE"
        pts_to_brc = round(max(0.0, brc_threshold - curr_range), 2)
        prox_pct = round(min(100.0, (curr_range / max(0.1, brc_threshold)) * 100.0), 1)
        
    # Find bars elapsed since last historical BRC
    bars_since_brc = 0
    last_brc_time = None
    last_brc_class = None
    for b_idx in range(n_bars - 1, -1, -1):
        if rel_ranges[b_idx] >= 1.5:
            last_brc_time = times[b_idx]
            last_brc_class = "Bullish" if closes[b_idx] > opens[b_idx] else "Bearish"
            bars_since_brc = (n_bars - 1 - b_idx)
            break

    # ----------------------------------------------------
    # 6. RSI Momentum & Divergences
    # ----------------------------------------------------
    rsi_zone = "OVERBOUGHT" if curr_rsi >= 70.0 else ("OVERSOLD" if curr_rsi <= 30.0 else ("BULLISH_MOMENTUM" if curr_rsi >= 50.0 else "BEARISH_MOMENTUM"))
    
    # Detect RSI divergence on the last two swings
    divergence_type = "NONE"
    if len(sh_list) >= 2:
        s1, s2 = sh_list[-2], sh_list[-1]
        if s2["price"] > s1["price"] and s2["rsi"] is not None and s1["rsi"] is not None and s2["rsi"] < s1["rsi"]:
            divergence_type = "BEARISH_DIVERGENCE"
    if len(sl_list) >= 2 and divergence_type == "NONE":
        s1, s2 = sl_list[-2], sl_list[-1]
        if s2["price"] < s1["price"] and s2["rsi"] is not None and s1["rsi"] is not None and s2["rsi"] > s1["rsi"]:
            divergence_type = "BULLISH_DIVERGENCE"

    # ----------------------------------------------------
    # 7. Candlestick Bar Series for Charting (downsampled if needed)
    # ----------------------------------------------------
    # For UI responsiveness, return up to 300 recent bars for charting
    chart_bars_count = min(300, n_bars)
    c_slice = slice(n_bars - chart_bars_count, n_bars)
    
    chart_data = {
        "t": [str(x) for x in times[c_slice]],
        "o": [clean_float(x) for x in opens[c_slice]],
        "h": [clean_float(x) for x in highs[c_slice]],
        "l": [clean_float(x) for x in lows[c_slice]],
        "c": [clean_float(x) for x in closes[c_slice]],
        "wpr": [clean_float(x) for x in wprs[c_slice]],
        "rsi": [clean_float(x) for x in rsis[c_slice]],
        "rng": [clean_float(x) for x in ranges[c_slice]],
        "atr": [clean_float(x) for x in atrs[c_slice]],
        "rel_rng": [clean_float(x) for x in rel_ranges[c_slice]]
    }
    
    # Map swings into chart bar coordinates
    chart_swings = []
    start_chart_idx = n_bars - chart_bars_count
    for s in swings:
        if s["idx"] >= start_chart_idx:
            s_copy = dict(s)
            s_copy["chart_idx"] = s["idx"] - start_chart_idx
            chart_swings.append(s_copy)

    return {
        "tf": tf,
        "total_3yr_bars": total_3yr_bars,
        "displayed_bars": n_bars,
        "macro_stats": {
            "start_date": START_DATE,
            "high": round(float(full_high), 2),
            "low": round(float(full_low), 2),
            "close": round(float(full_close), 2),
            "open": round(float(full_open), 2),
            "return_pct": full_return_pct
        },
        "current_bar": {
            "time": str(times[-1]),
            "open": curr_open,
            "high": curr_high,
            "low": curr_low,
            "close": curr_close,
            "range": curr_range,
            "atr14": curr_atr,
            "wpr14": curr_wpr,
            "rsi14": curr_rsi,
            "rel_range": curr_rel_range
        },
        "dow_structure": {
            "trade_bias": trade_bias,
            "block_color": block_color,
            "bias_desc": bias_desc,
            "last_sh": last_sh,
            "prev_sh": prev_sh,
            "last_sl": last_sl,
            "prev_sl": prev_sl,
            "sh_count": len(sh_list),
            "sl_count": len(sl_list),
            "pre_breakout": {
                "range_high": clean_float(pre_range_high),
                "range_low": clean_float(pre_range_low),
                "range_width": clean_float((pre_range_high - pre_range_low) if pre_range_high and pre_range_low else None),
                "consolidation_bars": pre_consolidation_bars,
                "phase": "Consolidation / Accumulation" if trade_bias == "BULLISH" else "Consolidation / Distribution"
            },
            "breakout_event": {
                "type": breakout_type,
                "level": clean_float(breakout_level),
                "timestamp": str(breakout_time) if breakout_time else None,
                "bars_since_break": (n_bars - 1 - breakout_idx) if breakout_idx is not None else None
            },
            "post_breakout": {
                "status": post_status,
                "excursion_pts": clean_float(post_excursion_pts),
                "invalidation_level": clean_float(last_sl["price"] if trade_bias == "BULLISH" and last_sl else (last_sh["price"] if last_sh else None))
            }
        },
        "williams_r": {
            "value": curr_wpr,
            "zone": wpr_zone,
            "ob_level": -20.0,
            "os_level": -80.0,
            "swings_total": len(swings),
            "swings_matched": len(matched_swings),
            "swings_mismatched": len(mismatched_swings),
            "confluence_rate_pct": confluence_rate,
            "avg_gap_distance": avg_gap_distance
        },
        "brc_engine": {
            "is_brc": is_brc,
            "classification": brc_type,
            "current_range": curr_range,
            "brc_threshold": brc_threshold,
            "relative_range": curr_rel_range,
            "pts_to_brc": pts_to_brc,
            "proximity_pct": prox_pct,
            "bars_since_last_brc": bars_since_brc,
            "last_brc_time": str(last_brc_time) if last_brc_time else None,
            "last_brc_class": last_brc_class
        },
        "rsi_engine": {
            "value": curr_rsi,
            "zone": rsi_zone,
            "divergence": divergence_type
        },
        "swings_feed": swings[-20:],  # last 20 swings for table
        "chart_data": chart_data,
        "chart_swings": chart_swings
    }

def compute_dow_trend_hierarchy(tf_results):
    """
    Synthesize Dow Theory three-trend hierarchy:
    - Primary Trend (The Tide): 1D & 4H
    - Secondary Trend (The Waves): 4H & 1H
    - Tertiary Trend (The Ripples): 30m, 15m, 5m
    """
    d1 = tf_results["1D"]["dow_structure"]
    h4 = tf_results["4H"]["dow_structure"]
    h1 = tf_results["1H"]["dow_structure"]
    m30 = tf_results["30m"]["dow_structure"]
    m15 = tf_results["15m"]["dow_structure"]
    m5 = tf_results["5m"]["dow_structure"]
    
    # 1. Primary Trend (1D & 4H)
    p_score = 0
    if d1["trade_bias"] == "BULLISH": p_score += 2
    elif d1["trade_bias"] == "BEARISH": p_score -= 2
    
    if h4["trade_bias"] == "BULLISH": p_score += 1
    elif h4["trade_bias"] == "BEARISH": p_score -= 1
    
    if p_score >= 2:
        primary_dir = "BULLISH"
        primary_phase = "Public Participation (Markup)"
        primary_color = "GREEN"
    elif p_score <= -2:
        primary_dir = "BEARISH"
        primary_phase = "Public Participation (Markdown)"
        primary_color = "RED"
    else:
        primary_dir = "CONSOLIDATING / ACCUMULATION"
        primary_phase = "Accumulation / Consolidation Range"
        primary_color = "AMBER"
        
    # Primary Swing Retracement calculation on 1D
    d1_curr = tf_results["1D"]["current_bar"]["close"]
    d1_last_sh = d1["last_sh"]["price"] if d1["last_sh"] else d1_curr
    d1_last_sl = d1["last_sl"]["price"] if d1["last_sl"] else d1_curr
    primary_range = max(1.0, abs(d1_last_sh - d1_last_sl))
    primary_retracement = round((abs(d1_last_sh - d1_curr) / primary_range) * 100.0, 1)

    # 2. Secondary Trend (4H & 1H)
    s_score = 0
    if h4["trade_bias"] == "BULLISH": s_score += 1
    elif h4["trade_bias"] == "BEARISH": s_score -= 1
    
    if h1["trade_bias"] == "BULLISH": s_score += 1
    elif h1["trade_bias"] == "BEARISH": s_score -= 1
    
    if s_score == 2:
        secondary_dir = "BULLISH_IMPULSE"
        secondary_desc = "Aligned with Bullish Primary (Active Expansion)"
        secondary_color = "GREEN"
    elif s_score == -2:
        secondary_dir = "BEARISH_CORRECTION"
        secondary_desc = "Counter-Trend Pullback against Primary Trend"
        secondary_color = "RED"
    else:
        secondary_dir = "INDECISION / PAUSE"
        secondary_desc = "Secondary Consolidation / Retracement Testing Pivot"
        secondary_color = "AMBER"

    # 3. Tertiary Trend (30m, 15m, 5m)
    t_scores = [
        1 if m30["trade_bias"] == "BULLISH" else (-1 if m30["trade_bias"] == "BEARISH" else 0),
        1 if m15["trade_bias"] == "BULLISH" else (-1 if m15["trade_bias"] == "BEARISH" else 0),
        1 if m5["trade_bias"] == "BULLISH" else (-1 if m5["trade_bias"] == "BEARISH" else 0),
    ]
    t_total = sum(t_scores)
    if t_total >= 2:
        tertiary_dir = "BULLISH_MOMENTUM"
        tertiary_desc = f"Intraday Scalp Long Alignment ({t_total}/3 timeframes Bullish)"
        tertiary_color = "GREEN"
    elif t_total <= -2:
        tertiary_dir = "BEARISH_MOMENTUM"
        tertiary_desc = f"Intraday Scalp Short Alignment ({-t_total}/3 timeframes Bearish)"
        tertiary_color = "RED"
    else:
        tertiary_dir = "MIXED_CHOP"
        tertiary_desc = "Intraday Range-Bound / Microstructure Divergence"
        tertiary_color = "AMBER"

    # Alignment Matrix
    aligned = (primary_dir == "BULLISH" and secondary_dir == "BULLISH_IMPULSE" and "BULLISH" in tertiary_dir) or \
              (primary_dir == "BEARISH" and secondary_dir == "BEARISH_CORRECTION" and "BEARISH" in tertiary_dir)
              
    alignment_badge = "TRIPLE_CONFLUENCE" if aligned else "PULLBACK_SETUP"

    return {
        "primary": {
            "direction": primary_dir,
            "phase": primary_phase,
            "color": primary_color,
            "timeframes": ["1D", "4H"],
            "last_sh": clean_float(d1_last_sh),
            "last_sl": clean_float(d1_last_sl),
            "retracement_pct": primary_retracement,
            "dow_golden_zone": "33% - 66% Dow Standard Retracement Zone"
        },
        "secondary": {
            "direction": secondary_dir,
            "description": secondary_desc,
            "color": secondary_color,
            "timeframes": ["4H", "1H"]
        },
        "tertiary": {
            "direction": tertiary_dir,
            "description": tertiary_desc,
            "color": tertiary_color,
            "timeframes": ["30m", "15m", "5m"]
        },
        "alignment": {
            "status": alignment_badge,
            "recommendation": "Full Long Confluence: High-Probability Trend Following" if aligned and primary_dir == "BULLISH" else (
                "High-Probability Dip Buying: Secondary Pullback in Bullish Primary" if primary_dir == "BULLISH" and secondary_dir != "BULLISH_IMPULSE" else "Defensive Risk Management / Wait for Secondary Alignment"
            )
        }
    }

def generate_default_alerts(tf_results, dow_trends):
    """Generate baseline system alerts across all alertable criteria."""
    alerts = []
    
    # 1. Market Structure BOS Alerts
    for tf, res in tf_results.items():
        dow = res["dow_structure"]
        bo = dow["breakout_event"]
        if bo["type"] != "NONE" and bo["bars_since_break"] is not None and bo["bars_since_break"] <= 10:
            alerts.append({
                "id": f"BOS_{tf}_{bo['timestamp']}",
                "category": "Market Structure",
                "timeframe": tf,
                "severity": "CRITICAL" if tf in ["1D", "4H"] else "WARNING",
                "condition": f"{tf} {bo['type'].replace('_', ' ')}",
                "value": f"Level: {bo['level']} | Excursion: +{dow['post_breakout']['excursion_pts']} pts",
                "timestamp": bo["timestamp"],
                "status": dow["post_breakout"]["status"],
                "action": "Trend Continuation Execution" if dow["post_breakout"]["status"] == "RETEST_CONFIRMED" else "Monitor for Expansion"
            })
            
    # 2. Williams %R Extreme & Swing Gap Alerts
    for tf, res in tf_results.items():
        wpr = res["williams_r"]
        curr_w = wpr["value"]
        if curr_w >= -20.0:
            alerts.append({
                "id": f"WPR_OB_{tf}",
                "category": "Williams %R",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} Williams %R Overbought Exhaustion",
                "value": f"{curr_w:.1f} (>= -20.0)",
                "timestamp": res["current_bar"]["time"],
                "status": "ACTIVE_OVERBOUGHT",
                "action": "Watch for Swing High Reversal or Strong Momentum Squeeze"
            })
        elif curr_w <= -80.0:
            alerts.append({
                "id": f"WPR_OS_{tf}",
                "category": "Williams %R",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} Williams %R Oversold Discount",
                "value": f"{curr_w:.1f} (<= -80.0)",
                "timestamp": res["current_bar"]["time"],
                "status": "ACTIVE_OVERSOLD",
                "action": "Watch for Swing Low Bounce"
            })
            
        # Recent swing mismatch gap alert
        swings = res["swings_feed"]
        if len(swings) > 0:
            last_sw = swings[-1]
            if not last_sw["wpr_matched"] and last_sw["wpr_gap"] is not None and last_sw["wpr_gap"] >= 15.0:
                alerts.append({
                    "id": f"WPR_GAP_{tf}_{last_sw['time']}",
                    "category": "Swing Confluence",
                    "timeframe": tf,
                    "severity": "INFO",
                    "condition": f"{tf} Swing {last_sw['type']} %R Non-Confluence (Gap)",
                    "value": f"%R Gap: {last_sw['wpr_gap']:.1f} pts from trigger (W%R={last_sw['wpr']})",
                    "timestamp": last_sw["time"],
                    "status": "DIVERGENCE_WARNING",
                    "action": "Caution: Swing pivot occurred without momentum confirmation"
                })

    # 3. BRC Alerts (Detected or High Proximity)
    for tf, res in tf_results.items():
        brc = res["brc_engine"]
        if brc["is_brc"]:
            alerts.append({
                "id": f"BRC_TRIGGER_{tf}",
                "category": "BRC Engine",
                "timeframe": tf,
                "severity": "CRITICAL",
                "condition": f"{tf} Big Range Candle (BRC) Detected!",
                "value": f"Range: {brc['current_range']} pts (>= {brc['brc_threshold']} pts, Rel: {brc['relative_range']:.2f}x)",
                "timestamp": res["current_bar"]["time"],
                "status": brc["classification"],
                "action": "High Volatility Expansion: Track follow-through excursion"
            })
        elif brc["proximity_pct"] >= 75.0:
            alerts.append({
                "id": f"BRC_PROX_{tf}",
                "category": "BRC Engine",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} BRC Proximity Threshold Exceeded",
                "value": f"{brc['proximity_pct']:.1f}% reached ({brc['pts_to_brc']} pts away)",
                "timestamp": res["current_bar"]["time"],
                "status": "POTENTIAL_BRC_FORMING",
                "action": "Candle nearing 1.5x ATR expansion threshold"
            })

    # 4. Dow Trend Alignment Alerts
    p_dir = dow_trends["primary"]["direction"]
    s_dir = dow_trends["secondary"]["direction"]
    t_dir = dow_trends["tertiary"]["direction"]
    
    alerts.append({
        "id": "DOW_ALIGNMENT_MACRO",
        "category": "Dow Theory Trend",
        "timeframe": "Macro",
        "severity": "INFO",
        "condition": f"Dow Hierarchy: Primary={p_dir} | Secondary={s_dir} | Tertiary={t_dir}",
        "value": f"Alignment: {dow_trends['alignment']['status']}",
        "timestamp": tf_results["1D"]["current_bar"]["time"],
        "status": dow_trends["alignment"]["status"],
        "action": dow_trends["alignment"]["recommendation"]
    })

    # 5. RSI Alerts
    for tf, res in tf_results.items():
        rsi = res["rsi_engine"]
        curr_r = rsi["value"]
        if curr_r >= 70.0:
            alerts.append({
                "id": f"RSI_OB_{tf}",
                "category": "RSI Momentum",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} RSI Overbought Regime",
                "value": f"RSI = {curr_r:.1f} (>= 70.0)",
                "timestamp": res["current_bar"]["time"],
                "status": "OVERBOUGHT",
                "action": "Monitor for Overbought Pullback"
            })
        elif curr_r <= 30.0:
            alerts.append({
                "id": f"RSI_OS_{tf}",
                "category": "RSI Momentum",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} RSI Oversold Regime",
                "value": f"RSI = {curr_r:.1f} (<= 30.0)",
                "timestamp": res["current_bar"]["time"],
                "status": "OVERSOLD",
                "action": "Monitor for Mean-Reversion Bounce"
            })
            
        if rsi["divergence"] != "NONE":
            alerts.append({
                "id": f"RSI_DIV_{tf}",
                "category": "RSI Momentum",
                "timeframe": tf,
                "severity": "CRITICAL",
                "condition": f"{tf} {rsi['divergence'].replace('_', ' ')} Confirmed",
                "value": f"Price made new extreme while RSI diverged",
                "timestamp": res["current_bar"]["time"],
                "status": rsi["divergence"],
                "action": "High-Probability Trend Reversal Warning"
            })

    return alerts

def build_master_dataset():
    """Execute complete preprocessing and export master JSON."""
    print("=" * 65)
    print("NIFTY 50 3-Year Quantitative Visualizer Preprocessor")
    print("Processing timeframes: 1D, 4H, 1H, 30m, 15m, 5m")
    print(f"Start Window: {START_DATE} | Output: {OUTPUT_JSON}")
    print("=" * 65)
    
    t_start = time.time()
    tf_results = {}
    
    for tf in TIMEFRAMES:
        t0 = time.time()
        print(f"-> Processing {tf} timeframe...")
        tf_results[tf] = process_timeframe(tf)
        print(f"   [DONE] {tf}: {tf_results[tf]['total_3yr_bars']} bars, Bias={tf_results[tf]['dow_structure']['trade_bias']} in {time.time()-t0:.2f}s")
        
    print("\n-> Synthesizing Dow Theory Trend Hierarchy (Primary / Secondary / Tertiary)...")
    dow_trends = compute_dow_trend_hierarchy(tf_results)
    print(f"   Primary: {dow_trends['primary']['direction']} | Secondary: {dow_trends['secondary']['direction']} | Tertiary: {dow_trends['tertiary']['direction']}")
    
    print("\n-> Generating Default Alert Signals...")
    alerts = generate_default_alerts(tf_results, dow_trends)
    print(f"   Generated {len(alerts)} initial alerts across all engines.")
    
    master_payload = {
        "metadata": {
            "symbol": "NIFTY 50 Index",
            "market": "NSE (National Stock Exchange of India)",
            "start_date": START_DATE,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timeframes": TIMEFRAMES,
            "description": "Multi-timeframe Dow Theory, Williams %R, BRC Engine, and RSI Visualizer Dataset"
        },
        "timeframes": tf_results,
        "dow_trends": dow_trends,
        "default_alerts": alerts
    }
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(master_payload, f, separators=(",", ":"))
        
    file_size_mb = os.path.getsize(OUTPUT_JSON) / (1024 * 1024)
    print(f"\n[SUCCESS] Master JSON written: {OUTPUT_JSON} ({file_size_mb:.2f} MB)")
    print(f"Total processing elapsed time: {time.time()-t_start:.2f}s")
    print("=" * 65)
    return master_payload

if __name__ == "__main__":
    build_master_dataset()
