FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p memories storage/uploads storage/jobs storage/temp

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:${APP_PORT}/api/health || exit 1

CMD ["sh", "-c", "gunicorn --workers ${WEB_CONCURRENCY:-2} --worker-class sync --bind 0.0.0.0:${APP_PORT:-8000} --access-logfile - --error-logfile - --log-level info web_app:app"]
