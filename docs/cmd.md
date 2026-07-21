- python -m venv .venv
- source .venv/bin/activate
- ./script/setup_venvs.sh
- ./script/run_all.sh

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

# Run all the services with a new terminal UI in vs code
```
Press Ctrl + Shift + P to open the VS Code Command Palette.

Type and select Tasks: Run Task.

Select Run All Services from the dropdown menu.

Select Continue without scanning the task output (if prompted).
```
