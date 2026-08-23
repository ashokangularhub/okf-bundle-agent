# Dockerfile for OKF Bundle Agent Service
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY okf_bundle/ ./okf_bundle/

# Create .env if not provided
RUN touch .env

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8002/health', timeout=5)"

# Run service
CMD ["python", "-m", "uvicorn", "src.service:app", "--host", "0.0.0.0", "--port", "8002"]
