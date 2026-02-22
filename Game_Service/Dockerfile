FROM python:3.12-slim

WORKDIR /app

# Install system deps (optional but helps some builds)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY Game_Service /app/Game_Service

ENV PYTHONPATH=/app
EXPOSE 8001

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "Game_Service.app.GameMain:app", "--bind", "0.0.0.0:8001", "--workers", "2"]