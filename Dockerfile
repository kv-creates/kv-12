FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
