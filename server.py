"""
NIFTY 50 Quantitative Visualizer Server
Lightweight multi-threaded HTTP server for serving the Visualizer Dashboard
and providing interactive REST APIs for dynamic user-configured alert evaluations.
"""

import os
import sys
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "nifty_3yr_data.json")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")

PORT = int(os.environ.get("PORT", 8888))
HOST = os.environ.get("HOST", "0.0.0.0")

# Cache data in memory for instantaneous responses
DATA_CACHE = None

def get_data():
    global DATA_CACHE
    if DATA_CACHE is None:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                DATA_CACHE = json.load(f)
        else:
            from engine import build_master_dataset
            DATA_CACHE = build_master_dataset()
    return DATA_CACHE

def evaluate_dynamic_alerts(user_cfg):
    """
    Evaluate alerts dynamically based on user-provided inputs:
    user_cfg can contain:
    - wpr_ob: float (e.g. -20.0 or -15.0)
    - wpr_os: float (e.g. -80.0 or -85.0)
    - wpr_gap_threshold: float (e.g. 15.0)
    - brc_multiple: float (e.g. 1.5)
    - brc_prox_threshold: float (e.g. 75.0)
    - rsi_ob: float (e.g. 70.0)
    - rsi_os: float (e.g. 30.0)
    - selected_tfs: list of str (e.g. ["1D", "4H", "1H", "30m", "15m", "5m"])
    """
    data = get_data()
    tf_data = data["timeframes"]
    dow_trends = data["dow_trends"]
    
    wpr_ob = float(user_cfg.get("wpr_ob", -20.0))
    wpr_os = float(user_cfg.get("wpr_os", -80.0))
    wpr_gap_thresh = float(user_cfg.get("wpr_gap_threshold", 15.0))
    brc_mult = float(user_cfg.get("brc_multiple", 1.5))
    brc_prox_thresh = float(user_cfg.get("brc_prox_threshold", 75.0))
    rsi_ob = float(user_cfg.get("rsi_ob", 70.0))
    rsi_os = float(user_cfg.get("rsi_os", 30.0))
    selected_tfs = user_cfg.get("selected_tfs", ["1D", "4H", "1H", "30m", "15m", "5m"])
    
    custom_alerts = []
    
    for tf in selected_tfs:
        if tf not in tf_data:
            continue
        res = tf_data[tf]
        bar = res["current_bar"]
        dow = res["dow_structure"]
        bo = dow["breakout_event"]
        
        # 1. Market Structure BOS alert
        if bo["type"] != "NONE" and bo["bars_since_break"] is not None and bo["bars_since_break"] <= 15:
            custom_alerts.append({
                "id": f"DYN_BOS_{tf}_{bo['timestamp']}",
                "category": "Market Structure (Dow)",
                "timeframe": tf,
                "severity": "CRITICAL" if tf in ["1D", "4H"] else "WARNING",
                "condition": f"{tf} {bo['type'].replace('_', ' ')}",
                "value": f"Level: {bo['level']} | Excursion: +{dow['post_breakout']['excursion_pts']} pts",
                "timestamp": bo["timestamp"],
                "status": dow["post_breakout"]["status"],
                "action": "Trend Continuation Execution" if dow["post_breakout"]["status"] == "RETEST_CONFIRMED" else "Monitor Breakout Expansion"
            })
            
        # 2. Williams %R user thresholds
        curr_w = bar["wpr14"]
        if curr_w >= wpr_ob:
            custom_alerts.append({
                "id": f"DYN_WPR_OB_{tf}",
                "category": "Williams %R",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} W%R Overbought (>= {wpr_ob})",
                "value": f"{curr_w:.1f} pts (Threshold: {wpr_ob})",
                "timestamp": bar["time"],
                "status": "OVERBOUGHT_TRIGGER",
                "action": "Overbought condition active: Look for swing exhaustion or momentum run"
            })
        elif curr_w <= wpr_os:
            custom_alerts.append({
                "id": f"DYN_WPR_OS_{tf}",
                "category": "Williams %R",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} W%R Oversold (<= {wpr_os})",
                "value": f"{curr_w:.1f} pts (Threshold: {wpr_os})",
                "timestamp": bar["time"],
                "status": "OVERSOLD_TRIGGER",
                "action": "Oversold condition active: Look for swing support bounce"
            })
            
        # 3. Swings Mismatch Gap Alert
        for sw in res["swings_feed"][-5:]:
            if not sw["wpr_matched"] and sw["wpr_gap"] is not None and sw["wpr_gap"] >= wpr_gap_thresh:
                custom_alerts.append({
                    "id": f"DYN_GAP_{tf}_{sw['time']}",
                    "category": "Swing Confluence",
                    "timeframe": tf,
                    "severity": "INFO",
                    "condition": f"{tf} Swing {sw['type']} Divergence / Gap >= {wpr_gap_thresh}",
                    "value": f"Gap: {sw['wpr_gap']:.1f} pts | Price: {sw['price']} | %R: {sw['wpr']}",
                    "timestamp": sw["time"],
                    "status": "MOMENTUM_GAP",
                    "action": f"Price swing made turning point without reaching {wpr_ob if sw['type']=='SH' else wpr_os}"
                })
                
        # 4. BRC Custom Threshold & Proximity
        curr_range = bar["range"]
        curr_atr = bar["atr14"]
        custom_brc_thresh = round(brc_mult * curr_atr, 2)
        dyn_is_brc = curr_range >= custom_brc_thresh
        dyn_prox_pct = round(min(100.0, (curr_range / max(0.1, custom_brc_thresh)) * 100.0), 1)
        dyn_pts_away = round(max(0.0, custom_brc_thresh - curr_range), 2)
        
        if dyn_is_brc:
            custom_alerts.append({
                "id": f"DYN_BRC_TRIG_{tf}",
                "category": "BRC Engine",
                "timeframe": tf,
                "severity": "CRITICAL",
                "condition": f"{tf} BRC Triggered ({brc_mult}x ATR)",
                "value": f"Range: {curr_range} pts >= {custom_brc_thresh} pts",
                "timestamp": bar["time"],
                "status": "BRC_ACTIVE",
                "action": "High Volatility Expansion candle confirmed"
            })
        elif dyn_prox_pct >= brc_prox_thresh:
            custom_alerts.append({
                "id": f"DYN_BRC_PROX_{tf}",
                "category": "BRC Engine",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} BRC Proximity Alert (>= {brc_prox_thresh}%)",
                "value": f"{dyn_prox_pct}% reached ({dyn_pts_away} pts away from {custom_brc_thresh})",
                "timestamp": bar["time"],
                "status": "BRC_APPROACHING",
                "action": "Candle nearing volatility expansion threshold"
            })
            
        # 5. RSI Custom Thresholds
        curr_r = bar["rsi14"]
        if curr_r >= rsi_ob:
            custom_alerts.append({
                "id": f"DYN_RSI_OB_{tf}",
                "category": "RSI Momentum",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} RSI Overbought (>= {rsi_ob})",
                "value": f"RSI: {curr_r:.1f}",
                "timestamp": bar["time"],
                "status": "RSI_OVERBOUGHT",
                "action": "Monitor for Overbought Pullback"
            })
        elif curr_r <= rsi_os:
            custom_alerts.append({
                "id": f"DYN_RSI_OS_{tf}",
                "category": "RSI Momentum",
                "timeframe": tf,
                "severity": "WARNING",
                "condition": f"{tf} RSI Oversold (<= {rsi_os})",
                "value": f"RSI: {curr_r:.1f}",
                "timestamp": bar["time"],
                "status": "RSI_OVERSOLD",
                "action": "Monitor for Oversold Bounce"
            })

    # 6. Dow Trend Macro Alert
    custom_alerts.append({
        "id": "DYN_DOW_TREND",
        "category": "Dow Theory Trend",
        "timeframe": "Macro",
        "severity": "INFO",
        "condition": f"Primary: {dow_trends['primary']['direction']} | Secondary: {dow_trends['secondary']['direction']} | Tertiary: {dow_trends['tertiary']['direction']}",
        "value": f"Alignment: {dow_trends['alignment']['status']}",
        "timestamp": tf_data["1D"]["current_bar"]["time"],
        "status": dow_trends["alignment"]["status"],
        "action": dow_trends["alignment"]["recommendation"]
    })

    return custom_alerts

class VisualizerHandler(BaseHTTPRequestHandler):
    def send_json(self, status_code, data):
        body = json.dumps(data, separators=(",", ":")).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def send_file_response(self, file_path, content_type):
        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found")
            return
        with open(file_path, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path in ["/", "/index.html"]:
            self.send_file_response(INDEX_HTML, "text/html; charset=utf-8")
        elif path == "/nifty_3yr_data.json":
            self.send_file_response(DATA_FILE, "application/json; charset=utf-8")
        elif path == "/api/data":
            data = get_data()
            self.send_json(200, data)
        elif path == "/api/status":
            self.send_json(200, {"status": "ok", "time": time.strftime("%Y-%m-%d %H:%M:%S")})
        else:
            # Check local file
            local_path = os.path.join(BASE_DIR, path.lstrip("/"))
            if os.path.exists(local_path) and os.path.isfile(local_path):
                ext = os.path.splitext(local_path)[1].lower()
                mime = "application/pdf" if ext == ".pdf" else "text/plain"
                self.send_file_response(local_path, mime)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/evaluate-alerts":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(length).decode("utf-8")
                user_cfg = json.loads(raw_body) if raw_body else {}
                alerts = evaluate_dynamic_alerts(user_cfg)
                self.send_json(200, {
                    "status": "success",
                    "user_config": user_cfg,
                    "total_alerts": len(alerts),
                    "alerts": alerts,
                    "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                self.send_json(500, {"error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server_address = (HOST, PORT)
    httpd = ThreadingHTTPServer(server_address, VisualizerHandler)
    print(f"==========================================================")
    print(f"NIFTY 50 Quantitative Visualizer Server Running")
    print(f"URL: http://localhost:{PORT}")
    print(f"Serving: {INDEX_HTML}")
    print(f"API: http://localhost:{PORT}/api/data")
    print(f"Alert API: http://localhost:{PORT}/api/evaluate-alerts")
    print(f"==========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
