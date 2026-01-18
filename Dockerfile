# Simple development Dockerfile for Django app
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (psycopg2 build deps)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Expose port
EXPOSE 8000

# Default environment (override in compose)
ENV DJANGO_DEBUG=True \
    DJANGO_ALLOWED_HOSTS=0.0.0.0,localhost \
    DB_NAME=stacktracker \
    DB_USER=postgres \
    DB_PASSWORD=postgres \
    DB_HOST=db \
    DB_PORT=5432

# Do not run migrations automatically per user request
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
