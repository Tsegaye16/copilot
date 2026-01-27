#!/bin/bash
# Start script for Render deployment

# Render sets PORT automatically, but we can use it
export PORT=${PORT:-10000}

# Start the application
exec uvicorn backend.main:app --host 0.0.0.0 --port $PORT
