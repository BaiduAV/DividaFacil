# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app
COPY . .

ENV LOG_LEVEL=INFO \
    APP_NAME="Splitwise Web" \
    STATIC_DIR=static \
    TEMPLATES_DIR=templates

EXPOSE 8000

CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000"]
