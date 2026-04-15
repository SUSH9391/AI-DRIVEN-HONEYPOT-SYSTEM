FROM python:3.12-slim

# Install system dependencies (prevents common build errors)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv (modern package manager)
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency file first (for caching)
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system "torch==2.3.1" --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
RUN uv pip install --system PyJWT
RUN uv pip install --system "redis[asyncio]==5.0.8"
RUN uv pip install --system .

# Copy application code
COPY src/ .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
