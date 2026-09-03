FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY lumen/ ./lumen/
COPY api/ ./api/
COPY demo/ ./demo/

# Create sibyl memory directory
RUN mkdir -p /root/.sibyl-memory

# Expose port
EXPOSE 8080

# Start server
CMD ["python", "api/server.py"]
