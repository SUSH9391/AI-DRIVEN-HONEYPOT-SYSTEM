FROM python:3.12-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Copy dependency files first (for caching)
COPY src/pyproject.toml .

# Install dependencies using uv (modern pyproject.toml)
RUN uv pip install --system .

# Copy application code
COPY src/ .

EXPOSE 8000

# Run app using uv
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]