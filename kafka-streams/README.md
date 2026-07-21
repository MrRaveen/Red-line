# Kafka Streams Microservice

> For detailed architectural explanation, deep-dive configurations, and production guides, refer to [docs/kafka-streams.md](../docs/kafka-streams.md).

---

## 1. Protobuf Compilation

### Compile from Service Root (`kafka-streams/`):
```bash
python -m grpc_tools.protoc -I=proto --python_out=. proto/log.proto
```

### Compile from Test Folder (`kafka-streams/test/`):
```bash
python -m grpc_tools.protoc -I=../proto --python_out=. ../proto/log.proto
```

---

## 2. Docker Execution (Recommended)

### Step 1: Build & Start Services
```bash
docker compose build
docker compose up -d
```

### Step 2: Create Kafka Topic
```bash
docker exec -it kafka kafka-topics --create \
  --topic graph-log-data \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

### Step 3: View Worker Logs
```bash
docker compose logs -f streamer-worker
```

### Step 4: Run Test Producer
```bash
cd test
python test-producer.py --count 5
```

---

## 3. Local Native Execution (Development)

### Step 1: Environment Setup & Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start Infrastructure (Kafka & Kafka UI only)
```bash
docker compose up -d kafka kafka-ui
```

### Step 3: Create Topic
```bash
docker exec -it kafka kafka-topics --create \
  --topic graph-log-data \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

### Step 4: Run Faust Worker
> *Note: Update broker in `run.py` to `kafka://localhost:9094` when running locally outside Docker.*

```bash
python run.py worker -l info
```

### Step 5: Run Test Producer
```bash
cd test
python test-producer.py --count 5
```

---

## 4. Quick CLI Testing

```bash
echo '{"job_service_name":"MyService","nodeName":"AgentNode"}' | \
docker exec -i kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic graph-log-data
```

---

## 5. UI Dashboard
- **Kafka UI**: [http://localhost:8080](http://localhost:8080)
