- Linux activation
  - python -m venv .venv
  - source .venv/bin/activate
- Windows configuration
  - python -m venv .venv
  - ./script/run_all.sh
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

# base docker
docker build -t redline-base:v1 -f Dockerfile.base .

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
