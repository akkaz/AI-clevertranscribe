#!/bin/bash
echo "Starting AI Transcriber App..."
echo "Open http://localhost:8000 in your browser"
./venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
