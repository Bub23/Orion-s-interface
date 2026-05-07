FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create memories directory
RUN mkdir -p memories

# Run Flask directly on 0.0.0.0:8000
CMD ["python", "web_app.py"]
