#!/bin/bash
set -e

echo "=== Starting Tor ==="
# Start tor and capture any errors
tor --RunAsDaemon 1 --SocksPort 9050 --Log "notice stdout" 2>&1 || {
    echo "ERROR: tor --RunAsDaemon failed, trying as debian-tor user..."
    su -s /bin/bash -c "tor --RunAsDaemon 1 --SocksPort 9050" debian-tor 2>&1 || {
        echo "ERROR: tor failed as debian-tor too. Trying without daemon mode..."
        su -s /bin/bash -c "tor --SocksPort 9050" debian-tor &
    }
}

# Wait for Tor to actually be ready (up to 60 seconds)
echo "=== Waiting for Tor to bootstrap ==="
for i in $(seq 1 60); do
    if python -c "
import socket
s = socket.socket()
s.settimeout(1)
try:
    s.connect(('127.0.0.1', 9050))
    s.close()
    exit(0)
except:
    exit(1)
" 2>/dev/null; then
        echo "Tor is ready on port 9050 (after ${i}s)"
        break
    fi
    if [ "$i" -eq 60 ]; then
        echo "WARNING: Tor did not start within 60s. Continuing anyway..."
    fi
    sleep 1
done

echo "=== Starting FastAPI Backend ==="
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT
