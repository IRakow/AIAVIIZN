# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY requirements.txt app.py ./
COPY templates templates/
COPY static static/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Run gunicorn with app.py
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 app:app