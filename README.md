# NIFTY 50 Quantitative Visualizer Terminal

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Market: NSE India](https://img.shields.io/badge/Market-NSE%20India-orange.svg)](https://www.nseindia.com/)
[![Timeframes: 1D to 5m](https://img.shields.io/badge/Timeframes-1D%20%7C%204H%20%7C%201H%20%7C%2030m%20%7C%2015m%20%7C%205m-brightgreen.svg)]()

An institutional-grade, multi-timeframe quantitative trading visualizer and algorithmic research terminal for the **NIFTY 50 Index (NSE India)** covering 3 years of historical session data (2023–2026).

Built with **Charles Dow Theory market structure**, **Williams %R momentum exhaustion**, **Big Range Candle (BRC) relative volatility**, and a **dynamic user-configurable alert dispatcher**.

---

## 🌟 Key Features

### 1. 📊 Continuous Multi-Timeframe Dow Theory Blocks (`1D`, `4H`, `1H`, `30m`, `15m`, `5m`)
* **Continuous Visual Cards:** Stacks macro to micro timeframes sequentially.
* **Trade Data Color Coding:** Automatic **GREEN** (Bullish Long bias) vs **RED** (Bearish Short bias) based on structural confirmation.
* **Pre-Breakout Structure:** Measures consolidation boundaries, range width (pts), compression duration (bars), and Dow phase.
* **Breakout Events:** Detects Bullish Break of Structure (BOS Long), Bearish BOS Short, and Change of Character (CHoCH).
* **Post-Breakout Structure:** Evaluates Maximum Favorable Excursion ($MFE$), retest verification ($\pm 0.25 \times ATR$), and invalidation levels.
* **Interactive Mini Candlestick Charts:** Integrated HTML5 Canvas charts with BOS levels and swing tags.

### 2. 📉 Williams %R Analytics & Visualization
* 14-period lookback across all six timeframes.
* Real-time gauges for Overbought ($\ge -20.0$), Oversold ($\le -80.0$), and Neutral momentum.
* Multi-timeframe wave charts and filterable data feed with CSV export.

### 3. ⚖️ Swings & %R Confluence Tracker ("How Far It Is" Gap Metric)
* Validates whether price swing pivots coincide with momentum exhaustion extremes.
* Quantifies momentum divergence when unconfirmed via the **Gap Distance Metric**:
  $$\Delta \%R(\text{SH}) = |-20.0 - W\%R|, \quad \Delta \%R(\text{SL}) = |W\%R - (-80.0)|$$

### 4. ⚡ BRC Engine & Proximity Tracker
* Identifies statistical volatility expansion candles where:
  $$\text{Relative\_Range} = \frac{\text{Range}}{\text{ATR}_{14}} \ge 1.50$$
* **"How Far It Is If Not Found" (Normal Candle Proximity):**
  * **Points Needed to Reach BRC:** $\Delta \text{Pts} = \max(0, 1.5 \times \text{ATR}_{14} - \text{Range})$
  * **Proximity % Reached:** $\text{Proximity}\% = \min\left(100.0, \frac{\text{Range}}{1.5 \times \text{ATR}_{14}} \times 100.0\right)$
  * **Compression Counter:** Bars elapsed since last confirmed BRC (identifying squeeze breakouts when $\ge 12$ bars).

### 5. 🏛️ Dow Theory Trend Hierarchy Command Center
* **Primary Trend (The Tide):** Macro regime on **1D** and **4H** (Direction, Phase, Swing High/Low, Retracement Depth).
* **Secondary Trend (The Waves):** Intermediate pullbacks on **4H** and **1H** (aligned impulse vs counter-trend reaction within the Dow 33%–66% Golden Zone).
* **Tertiary Trend (The Ripples):** Intraday execution setups on **30m**, **15m**, and **5m**.
* **Triple Confluence Indicator:** Institutional alignment scoring across all tiers.

### 6. 📈 RSI Momentum Engine
* Wilder's 14-period RSI across all timeframes.
* Overbought ($\ge 70$), Oversold ($\le 30$), and 50 centerline bull/bear momentum split.
* Scanner for regular bullish and bearish swing divergences.

### 7. 🔔 User-Configurable Alert Generation Center
* **Custom Parameter Inputs:** Adjust Williams %R thresholds, Swing gap limits, BRC ATR multiples, BRC proximity %, and RSI boundaries.
* **Dynamic Evaluation:** One-click re-evaluation across the entire 3-year multi-timeframe dataset.
* **Live Feed & Export:** Severity badges (`CRITICAL`, `WARNING`, `INFO`), triggered timestamps, execution actions, and CSV export.

---

## 📁 Repository Structure

```
.
├── index.html                                  # Master Visualizer Single-Page Application (SPA)
├── engine.py                                    # Quantitative preprocessor & analytical engine
├── server.py                                    # Multi-threaded Python server & REST API
├── nifty_3yr_data.json                          # Precomputed 3-year high-density dataset (214 KB)
├── run_visualizer.bat                           # 1-click Windows launcher
├── Dockerfile                                   # Docker container specification
├── docker-compose.yml                           # Docker Compose orchestration
├── Procfile                                     # Cloud PaaS deployment rule (Render/Railway)
├── nifty-visualizer.service                     # Systemd service daemon for Linux VPS
├── nginx-visualizer.conf                        # Nginx reverse proxy config with SSL & Gzip
├── DEPLOYMENT.md                                # Comprehensive multi-environment deployment guide
├── NIFTY50_Visualizer_End_to_End_Process.pdf    # Executive End-to-End Engineering Report
├── NIFTY50_Visualizer_Methodology_and_Formulas.pdf # Mathematical & Algorithmic Formulas Specification
└── requirements.txt                             # Python dependencies
```

---

## 🚀 Quick Start (Local)

### Windows
Double-click `run_visualizer.bat` or run:
```cmd
python engine.py
python server.py
```
Open [http://localhost:8888](http://localhost:8888) in your browser.

### Linux / Mac
```bash
pip install -r requirements.txt
python3 engine.py
python3 server.py
```

---

## 🐳 Docker Deployment

```bash
docker build -t nifty-visualizer .
docker run -d -p 8888:8888 --name nifty_terminal nifty-visualizer
```
Or using Docker Compose:
```bash
docker compose up -d
```

---

## ☁️ Cloud & GitHub Pages Deployment

* **Cloud PaaS (Render / Railway):** Push to GitHub and deploy via the included `Procfile`.
* **GitHub Pages (Serverless):** Go to **Settings &rarr; Pages &rarr; Source: main / (root)**. The terminal operates 100% client-side with full offline evaluation!
* **Linux VPS (Ubuntu / Debian):** Use the included `nifty-visualizer.service` and `nginx-visualizer.conf`. See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions.

---

## 📄 Documentation

* [NIFTY50_Visualizer_End_to_End_Process.pdf](NIFTY50_Visualizer_End_to_End_Process.pdf) — Complete architectural and engineering walkthrough.
* [NIFTY50_Visualizer_Methodology_and_Formulas.pdf](NIFTY50_Visualizer_Methodology_and_Formulas.pdf) — Formal mathematical definitions, equations, and algorithms.

---

## 📜 License
MIT License. Free for research and educational quantitative trading analysis.
