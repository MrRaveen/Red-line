#for the production "release" branch use only. Use docker-compose 
#file natively for the development

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py", "worker", "-l", "info"]

