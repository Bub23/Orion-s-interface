FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create memories directory
RUN mkdir -p memories

# Default command: run interactive shell or script
CMD ["python", "main.py"]
