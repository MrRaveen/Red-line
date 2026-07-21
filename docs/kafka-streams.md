# Kafka Streams Service Documentation

This document provides a comprehensive guide for setting up, developing, testing, and deploying the `kafka-streams` microservice. The service uses **Faust** (a Python stream processing library) and **Google Protocol Buffers (Protobuf)** to process log data streams sent over **Apache Kafka**.

---

## 1. Overview & Architecture

### Components
- **Kafka Broker**: Single-node Kafka container running in KRaft mode (`cp-kafka:7.6.1`).
- **Kafka UI**: Web dashboard for inspecting Kafka topics, partitions, and messages (`provectuslabs/kafka-ui:latest`) running on port `8080`.
- **Faust Worker (`streamer-worker`)**: Asynchronous worker consuming Protobuf binary messages from the `graph-log-data` topic.
- **Protobuf Schema (`proto/log.proto`)**: Defines the structured `Log` event payload.

### Network & Listeners Setup
- **`INTERNAL` (`kafka:9092`)**: Used for inter-container communication inside the Docker network (e.g., Faust worker, Kafka UI).
- **`EXTERNAL` (`localhost:9094`)**: Used for host machine connections (e.g., host test scripts, local producers).

---

## 2. Prerequisites & Local Environment Setup

### 2.1 Virtual Environment Setup
From the project root:

```bash
# Create and activate Python virtual environment
python -m venv .venv
source .venv/bin/activate

# Execute repository setup scripts if available
./script/setup_venvs.sh
```

### 2.2 Install Dependencies
Navigate to `kafka-streams/` and install required dependencies:

```bash
cd kafka-streams
pip install -r requirements.txt
```

*`requirements.txt` dependencies:*
- `faust-streaming`: Faust stream processing framework.
- `confluent-kafka`: Kafka client for Python.
- `protobuf`: Protocol Buffers runtime library.
- `grpcio-tools`: Protobuf compiler tools for generating Python bindings.

---

## 3. Protocol Buffers (gRPC/Protobuf) Compilation

Whenever changes are made to `proto/log.proto`, the Python protobuf bindings (`log_pb2.py`) must be generated.

### 3.1 Compile for `kafka-streams/` Root
Run from the `kafka-streams/` root folder:

```bash
python -m grpc_tools.protoc \
  -I=proto \
  --python_out=. \
  proto/log.proto
```

### 3.2 Compile for `kafka-streams/test/` Folder
Run from the `kafka-streams/test/` folder if testing separately:

```bash
python -m grpc_tools.protoc \
  -I=../proto \
  --python_out=. \
  ../proto/log.proto
```

---

## 4. Kafka Topic Management

### Creating the `graph-log-data` Topic
After starting Kafka, create the required topic with 3 partitions and a replication factor of 1:

```bash
docker exec -it kafka kafka-topics --create \
  --topic graph-log-data \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

---

## 5. Development Guide

### 5.1 Local Containerized Execution (Docker Compose)
During development, services are run using Docker Compose with volume mounts (`.:/app`) for live code editing.

```bash
# Build containers
docker compose build

# Start services in detached mode
docker compose up -d

# View Faust worker logs
docker compose logs -f streamer-worker
```

### 5.2 Local Native Execution (Without Docker for Worker)
To run the Faust worker directly on your host machine for active debugging:

1. Ensure Kafka is running (`docker compose up -d kafka`).
2. Update broker URL in `run.py` to `kafka://localhost:9094` for local host access.
3. Run the Faust application:

```bash
python run.py worker -l info
```

---

## 6. Testing & Verification

### 6.1 Running the Test Producer
A test script (`test/test-producer.py`) sends Protobuf-encoded test events to Kafka over `localhost:9094`.

```bash
cd test
python test-producer.py --count 5
```

### 6.2 Monitoring & Verification
- **Logs**: Monitor Faust logs to verify deserialization:
  ```bash
  docker compose logs -f streamer-worker
  ```
  *Expected Output snippet:*
  ```text
  [node-0] service_name=test-service
  ```
- **Kafka UI**: Open `http://localhost:8080` in your web browser to view active topics, message offsets, and partition distributions.

### 6.3 Manual CLI Producer Testing
To push raw test messages via CLI:

```bash
echo '{"job_service_name":"MyService","nodeName":"AgentNode"}' | \
docker exec -i kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic graph-log-data
```

---

## 7. Production Deployment Guide

### 7.1 Production Dockerfile
The production image uses a multi-stage or slim python runtime (`python:3.10-slim`).

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py", "worker", "-l", "info"]
```

### 7.2 Root-Level Pipeline Orchestration
For release/production builds:
1. Build the production Docker image:
   ```bash
   docker build -t kafka-streams-worker:latest .
   ```
2. In production orchestration (e.g., Kubernetes or root-level Compose), disable host-exposed listener ports (`9094`) and restrict Kafka access to internal container networks (`kafka:9092`).
3. Set environment variable logs to `WARNING` or `ERROR` for production efficiency (`-l warning`).
