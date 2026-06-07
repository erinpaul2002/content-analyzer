#!/bin/bash

echo "Starting Tor..."
tor --RunAsDaemon 1

echo "Starting Privoxy..."
privoxy /etc/privoxy/config

# Give Tor a few seconds to bootstrap
sleep 5

echo "Starting FastAPI Backend..."
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT
