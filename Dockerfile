FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000

# Run API or worker depending on ENV
CMD ["sh", "-c", "if [ \"$SERVICE\" = 'worker' ]; then celery -A celery_worker worker --loglevel=info; else uvicorn main:app --host 0.0.0.0 --port $PORT; fi"]
