FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install uv

# Install CPU-only torch FIRST to prevent uv pulling CUDA variant
# CPU torch = ~200MB vs CUDA torch = ~2.5GB
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY pyproject.toml .
COPY uv.lock* .

# --no-install-package torch tells uv to skip torch (already installed above)
RUN uv sync --frozen --no-dev --no-install-package torch

# Pre-cache the ML model during build
RUN uv run python -c "from transformers import pipeline; pipeline('text-classification', model='martin-ha/toxic-comment-model', device=-1)"

COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
