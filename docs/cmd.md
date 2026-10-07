- Linux activation
  - python -m venv .venv
  - source .venv/bin/activate
- Windows configuration
  - python -m venv .venv
  - .\.venv\Scripts\Activate.ps1


- Create a testing topic (kafka-stream)
docker exec -it kafka kafka-topics --create \
  --topic graph-log-data \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

- GRPC compiling from the root of the lafka-stream
python -m grpc_tools.protoc \
  -I=proto \
  --python_out=. \
  proto/log.proto  

- GRPC compile from the test folder of the kafka stream
python -m grpc_tools.protoc \
  -I=../proto \
  --python_out=. \
  ../proto/log.proto  

- build
docker compose build
- run
docker compose up -d  
- test the producer with the protobuf payload
cd "test"
python test-producer.py

- PI test run (lang graph)
cd prompt_injection_attack
python -m app.graphs.main_graph.nodes
python -m app.graphs.main_graph.fakeLLM
python -m app.graphs.main_graph.kafka_beta.consumer
python -m app.graphs.main_graph.kafka_beta.log_processor.main
python -m app.graphs.main_graph.agents_beta
# Navigate to the judge_agent directory (or root, if you set pythonpath)
# Make sure your virtual environment is activated, if any
python -m judge_agent.tests.test_judge_out_topic

- realtime service testing new
E:\Work\College_works\Competitions\IEEE_young_protege\code\Red-line\realtime_data_service> flask run
(.venv) PS E:\Work\College_works\Competitions\IEEE_young_protege\code\Red-line\realtime_data_service> python -m app.consumer.v1_consumer

PS C:\Users\Ravin>  python -c "from kafka import KafkaProducer; import json; producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'], value_serializer=lambda v: json.dumps(v).encode('utf-8')); producer.send('results_out', {'message': 'Hello ravin bro', 'status': 'success'}); producer.flush()"
PS C:\Users\Ravin>

curl.exe -N http://127.0.0.1:5000/api/v1/stream

# base docker
![alt text](image-9.png)

#remove laftovers
docker exec red-line-kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list | Select-String -Pattern '^__' -NotMatch | ForEach-Object { $topic = $_.ToString().Trim(); if ($topic) { docker exec red-line-kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic $topic } }

python test_saga_workflow_pi.py
python test_saga_workflow_pii.py
python test_saga_workflow_jailbreak.py
python test_saga_workflow_hallucination.py

# Run all the services with a new terminal UI in vs code
```
Press Ctrl + Shift + P to open the VS Code Command Palette.

Type and select Tasks: Run Task.

Select Run All Services from the dropdown menu.

Select Continue without scanning the task output (if prompted).
```

curl -X POST "http://localhost:8001/api/v1/start-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "userID": "ravin",
    "targetURL": "http://host.docker.internal:4000/api/generate",
    "job_name": "test",
    "workflowID": "prompt_injection_v1",
    "description": "test2"
  }'

curl -X POST "http://localhost:8001/api/v1/start-workflow"   -H "Content-Type: application/json"   -d '{
    "userID": "ravin",
    "targetURL": "http://host.docker.internal:4000/api/generate",
    "job_name": "mango",
    "workflowID": "prompt_injection_v1",
    "description": "buntop1223"
  }'


⚠️ On Linux (Not Your Case)

On native Linux Docker (not Docker Desktop), host.docker.internal does not exist by default. That's why Linux users must add:
yaml

extra_hosts:
  - "host.docker.internal:host-gateway"

This tells Docker to map host.docker.internal to the host's gateway IP.
