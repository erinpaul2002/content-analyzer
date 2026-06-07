FROM python:3.10-slim

# Install Tor and Privoxy
RUN apt-get update && \
    apt-get install -y tor privoxy && \
    rm -rf /var/lib/apt/lists/*

# Configure Privoxy to forward all traffic through Tor's SOCKS5 proxy
RUN echo "forward-socks5t / 127.0.0.1:9050 ." >> /etc/privoxy/config

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code
COPY . .

# Copy start script and ensure it is executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Render dynamically assigns the PORT environment variable
EXPOSE 8000

# Start Tor, Privoxy, and the FastAPI backend
CMD ["/app/start.sh"]
