
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GUNICORN_CMD_ARGS="--workers=4 --worker-class=uvicorn.workers.UvicornWorker --timeout=120 --keep-alive=60"

CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000"]