FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install uv

# Install CPU-only torch FIRST (~200MB)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY pyproject.toml .
COPY uv.lock* .

RUN uv sync --frozen --no-dev --no-install-package torch

COPY . .

# Pre-cache ML model (~250MB baked in)
RUN uv run python -c "\
    from transformers import pipeline; \
    pipeline('text-classification', \
             model='martin-ha/toxic-comment-model', \
             device=-1)"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

