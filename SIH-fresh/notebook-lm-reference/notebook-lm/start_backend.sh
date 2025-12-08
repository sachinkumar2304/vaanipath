#!/bin/bash

# Start backend script for NotebookLM clone

echo "Starting NotebookLM Backend..."

# Activate virtual environment
source .venv/bin/activate

# Start FastAPI server
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
