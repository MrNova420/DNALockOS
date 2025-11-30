#!/bin/bash
# ==============================================================================
# DNALockOS - DNA-Key Authentication System
# Copyright (c) 2025 WeNova Interactive
# ==============================================================================
#
# OWNERSHIP: Kayden Shawn Massengill (Operating as WeNova Interactive)
#
# COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE
#
# This is proprietary commercial software. A valid commercial license is
# required for ANY use. Unauthorized use, copying, modification, or
# distribution is strictly prohibited and will be prosecuted.
#
# For licensing inquiries: WeNova Interactive
# ==============================================================================

# DNALockOS Startup Script
# Starts all required services for the DNA-Key Authentication System

set -e

echo "Starting DNALockOS..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Start the API server
echo "Starting API server on http://localhost:8000"
python3 -m uvicorn server.api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

echo ""
echo "DNALockOS is running!"
echo "  API Server: http://localhost:8000"
echo "  API Docs:   http://localhost:8000/api/docs"
echo "  Health:     http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $API_PID 2>/dev/null; exit" INT TERM
wait