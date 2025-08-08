# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy the rest of the application
COPY . .

# Create templates directory if it doesn't exist
RUN mkdir -p templates static

# Make sure the app is executable
RUN chmod +x app.py

# Expose the port Cloud Run expects
EXPOSE 8080

# Run the application with gunicorn for production
# Cloud Run expects the app to listen on $PORT
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app