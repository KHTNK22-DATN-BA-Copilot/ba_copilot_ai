#!/bin/bash
set -e

echo "Starting Mermaid Validator Service..."
cd /app/services/mermaid_validator/nodejs
PORT=51234 HOST=localhost node server.js &
VALIDATOR_PID=$!
echo "Validator started with PID: $VALIDATOR_PID on port 51234"

# Wait for validator to be ready
echo "Waiting for validator to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:51234/health >/dev/null 2>&1; then
        echo "Validator is ready!"
        break
    fi
    echo "Attempt $i/30: Validator not ready yet..."
    sleep 1
done

cd /app
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
