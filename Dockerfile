FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure data json exists or build it
RUN python -c "import os; print('Checking data...'); exit(0 if os.path.exists('nifty_3yr_data.json') else 1)" || python engine.py

# Expose port (default 8888, configurable via PORT env)
ENV PORT=8888
ENV HOST=0.0.0.0
EXPOSE 8888

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8888/api/status || exit 1

# Start server
CMD ["python", "-u", "server.py"]
