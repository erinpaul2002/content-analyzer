#!/bin/bash

echo "Starting Tor..."
tor --RunAsDaemon 1 --SocksPort 9050

# Wait for Tor to bootstrap
echo "Waiting for Tor to bootstrap..."
for i in $(seq 1 30); do
    if python -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('127.0.0.1', 9050)); s.close()" 2>/dev/null; then
        echo "Tor is ready on port 9050."
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 1
done

echo "Starting FastAPI Backend..."
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT
