FROM python:3.10-slim

# Install Tor
RUN apt-get update && \
    apt-get install -y tor && \
    rm -rf /var/lib/apt/lists/*

# Fix Tor permissions so it can start in a container
RUN mkdir -p /var/lib/tor /var/log/tor /run/tor && \
    chown -R debian-tor:debian-tor /var/lib/tor /var/log/tor /run/tor

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

# Start Tor and the FastAPI backend
CMD ["/app/start.sh"]
