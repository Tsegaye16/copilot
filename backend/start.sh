#!/bin/bash
# Start script for Render deployment
# This script ensures the correct Python path is set

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the backend directory
cd "$SCRIPT_DIR"

# Set PYTHONPATH to include the backend directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Start uvicorn
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
