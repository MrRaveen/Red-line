FROM python:3.11-slim

WORKDIR /app

COPY prompt_injection_attack_new/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY prompt_injection_attack_new/app/ ./app/
COPY prompt_injection_attack_new/wsgi.py .
COPY prompt_injection_attack_new/run.py .
COPY common/ ./common/

CMD ["gunicorn", "--bind", "0.0.0.0:8005", "wsgi:app"]