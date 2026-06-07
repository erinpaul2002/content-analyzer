#!/bin/bash

echo "Setting up permissions..."
mkdir -p /var/log/privoxy /var/run/privoxy
chown -R privoxy:privoxy /var/log/privoxy /var/run/privoxy /etc/privoxy

echo "Starting Tor..."
su -s /bin/bash -c "tor > /dev/null" debian-tor &

echo "Starting Privoxy..."
privoxy --no-daemon /etc/privoxy/config &

# Give Tor a few seconds to bootstrap
sleep 5

echo "Starting FastAPI Backend..."
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT
