FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Create memories directory
RUN mkdir -p memories

# Run with Gunicorn: 4 workers, bind to 0.0.0.0:8000
CMD ["gunicorn", "--workers", "4", "--worker-class", "sync", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "web_app:app"]
