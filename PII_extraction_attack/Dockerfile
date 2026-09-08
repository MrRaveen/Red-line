FROM python:3.11-slim

WORKDIR /app

COPY PII_extraction_attack/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY PII_extraction_attack/app/ ./app/
COPY PII_extraction_attack/wsgi.py .
COPY PII_extraction_attack/run.py .
COPY common/ ./common/

CMD ["gunicorn", "--bind", "0.0.0.0:8002", "wsgi:app"]
