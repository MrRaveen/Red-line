FROM redline-base:v1

WORKDIR /app

COPY judge_agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY judge_agent/app/ ./app/
COPY judge_agent/wsgi.py .
COPY judge_agent/run.py .
COPY common/ ./common/
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]