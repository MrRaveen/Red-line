FROM redline-base:v1

WORKDIR /app

COPY hallucination_attack/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hallucination_attack/app/ ./app/
COPY hallucination_attack/wsgi.py .
COPY hallucination_attack/run.py .
COPY common/ ./common/

CMD ["gunicorn", "--bind", "0.0.0.0:8004", "wsgi:app"]