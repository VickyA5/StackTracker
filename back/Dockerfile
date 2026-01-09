FROM python:3.12-slim

# Runtime basics
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (for common Python packages like psycopg, uvicorn, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl wget build-essential && \
  rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

EXPOSE 8000

# Simple default: run uvicorn (compose may override with --reload in dev)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]