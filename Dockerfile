# Multi-stage Dockerfile for Localisation Engine

# Stage 1: Base image with system dependencies
FROM python:3.10-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: Python dependencies
FROM base as dependencies

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies as app

# Copy application code
COPY . .

# Create storage directory
RUN mkdir -p storage/jobs storage/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STORAGE_ROOT=/app/storage
ENV DATABASE_URL=sqlite:///./localisation_engine.db

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



