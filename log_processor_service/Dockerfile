FROM redline-base:v1

WORKDIR /app

COPY log_processor_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY log_processor_service/app/ ./app/
COPY common/ ./common/

CMD ["python", "-m", "app.consumer.v1_consumer"]
