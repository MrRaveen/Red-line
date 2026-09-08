FROM redline-base:v1

WORKDIR /app

COPY SAGA_orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY SAGA_orchestrator/app/ ./app/
COPY SAGA_orchestrator/wsgi.py .
COPY SAGA_orchestrator/run.py .
COPY SAGA_orchestrator/run_worker.py .
COPY common/ ./common/

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "wsgi:app"]
