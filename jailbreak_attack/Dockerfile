FROM redline-base:v1

WORKDIR /app

COPY jailbreak_attack/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jailbreak_attack/app/ ./app/
COPY jailbreak_attack/wsgi.py .
COPY jailbreak_attack/run.py .
COPY common/ ./common/

CMD ["gunicorn", "--bind", "0.0.0.0:8003", "wsgi:app"]
