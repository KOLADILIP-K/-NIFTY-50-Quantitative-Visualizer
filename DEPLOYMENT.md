# NIFTY 50 Quantitative Visualizer — Deployment Guide

This guide provides step-by-step instructions for deploying the **NIFTY 50 Quantitative Visualizer Terminal** across multiple environments, from your local Windows workstation to free cloud platforms and production cloud VPS instances.

---

## Deployment Architecture Overview

The visualizer consists of two lightweight layers:
1. **Frontend Terminal (`index.html`)**: Single-page application (SPA) with zero external CDN dependencies, embedding interactive HTML5 Canvas charts, 7 analytical tabs, and an alert generation dispatcher.
2. **Backend Engine (`server.py` & `engine.py`)**: Multi-threaded Python server that serves the precompiled master cache (`nifty_3yr_data.json`) and handles dynamic `/api/evaluate-alerts` POST requests.

Because `index.html` also includes full client-side JavaScript evaluation fallback, **the application can be deployed either with a Python backend OR as a 100% static serverless website.**

---

## Option 1: Local & LAN Deployment (Windows Workstation)

Best for immediate personal trading analysis and local network sharing.

### A. One-Click Launch
1. Open the visualizer directory: `d:\KOLADILIP K\PI\visualizer`.
2. Double-click **`run_visualizer.bat`**.
3. The script automatically:
   - Verifies the preprocessed `nifty_3yr_data.json` dataset.
   - Starts the server on port `8888`.
   - Opens `http://localhost:8888` in your default browser.

### B. Accessing from Other Devices on your Local Network (LAN)
1. Find your Windows computer's local IP address:
   ```cmd
   ipconfig
   ```
   *(Look for `IPv4 Address`, e.g., `192.168.1.15`)*.
2. Ensure Windows Firewall allows inbound connections on port `8888`:
   ```powershell
   New-NetFirewallRule -DisplayName "NIFTY Visualizer" -Direction Inbound -LocalPort 8888 -Protocol TCP -Action Allow
   ```
3. Open `http://<YOUR_LAN_IP>:8888` from your mobile phone, tablet, or laptop on the same Wi-Fi.

---

## Option 2: Cloud PaaS Deployment (Render / Railway / Fly.io)

Best for 24/7 web access with automated SSL and zero server maintenance.

### Deploying on Render (Free Tier)
1. Initialize a Git repository in `visualizer`:
   ```bash
   cd "d:\KOLADILIP K\PI\visualizer"
   git init
   git add .
   git commit -m "Deploy NIFTY 50 Visualizer"
   ```
2. Push your repository to **GitHub** (public or private).
3. Log in to [Render.com](https://render.com) and click **New + &rarr; Web Service**.
4. Connect your GitHub repository.
5. Configure the build settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python engine.py`
   - **Start Command:** `python -u server.py`
   - **Plan:** Free or Starter
6. Click **Deploy Web Service**. Render provides a public URL (e.g., `https://nifty50-visualizer.onrender.com`) with automated HTTPS!

---

## Option 3: Docker & Docker Compose

Best for containerized cloud servers and consistent deployment.

### A. Single Docker Command
```bash
docker build -t nifty-visualizer .
docker run -d --name nifty_terminal -p 8888:8888 --restart unless-stopped nifty-visualizer
```
The terminal is now live at `http://localhost:8888`.

### B. Using Docker Compose
Run directly with the included `docker-compose.yml`:
```bash
docker compose up -d
```
To view logs:
```bash
docker compose logs -f
```
To stop the container:
```bash
docker compose down
```

---

## Option 4: Production Linux Cloud VPS (Ubuntu 22.04 / 24.04 LTS)

Best for institutional hosting on DigitalOcean, AWS EC2, Google Cloud, or Linode with a custom domain and SSL.

### Step 1: Transfer Project to VPS
```bash
# On your local machine:
scp -r "d:\KOLADILIP K\PI\visualizer" user@your_vps_ip:/var/www/nifty-visualizer
```

### Step 2: Install Python & Dependencies on VPS
```bash
sudo apt update && sudo apt install -y python3 python3-pip nginx certbot python3-certbot-nginx
cd /var/www/nifty-visualizer
pip install -r requirements.txt
python3 engine.py
```

### Step 3: Configure Systemd Background Service
Copy the provided service file:
```bash
sudo cp nifty-visualizer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nifty-visualizer
sudo systemctl start nifty-visualizer
sudo systemctl status nifty-visualizer
```

### Step 4: Configure Nginx & SSL
Copy the provided Nginx configuration:
```bash
sudo cp nginx-visualizer.conf /etc/nginx/sites-available/nifty-visualizer
# Edit the domain name inside the file:
sudo nano /etc/nginx/sites-available/nifty-visualizer
sudo ln -s /etc/nginx/sites-available/nifty-visualizer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Obtain a free SSL certificate from Let's Encrypt:
```bash
sudo certbot --nginx -d nifty.yourdomain.com
```

Your visualizer is now securely accessible worldwide at `https://nifty.yourdomain.com`.

---

## Option 5: 100% Serverless Static Hosting (GitHub Pages / Cloudflare Pages / Netlify)

Because `index.html` includes client-side evaluation fallback, you can host it as a completely static web app for free:

1. Copy `index.html` and `nifty_3yr_data.json` to your repository's root.
2. In GitHub, go to **Settings &rarr; Pages &rarr; Branch: main &rarr; Folder: / (root) &rarr; Save**.
3. Within 60 seconds, your visualizer will be live at:
   `https://<your-username>.github.io/<repo-name>/`

All charts, multi-timeframe Dow structure cards, Williams %R gauges, BRC proximity trackers, and alert evaluations function client-side in the browser!
