- python -m venv .venv
- source .venv/bin/activate
- ./script/setup_venvs.sh
- ./script/run_all.sh

docker exec -it kafka kafka-topics --create \
  --topic graph-log-data \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

- GRPC compiling 
python -m grpc_tools.protoc \
  -I=proto \
  --python_out=. \
  proto/event.proto  

# Run all the services with a new terminal UI in vs code
```
Press Ctrl + Shift + P to open the VS Code Command Palette.

Type and select Tasks: Run Task.

Select Run All Services from the dropdown menu.

Select Continue without scanning the task output (if prompted).
```
