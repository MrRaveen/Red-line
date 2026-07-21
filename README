# Red-line

## Project Setup (Local Development)

> **Note:** The Docker-based deployment configuration is currently a work in progress and not fully created yet. Please use the following local setup instructions to run the project.

### 1. Backend Environment Setup

First, you need to create virtual environments and install dependencies for all Python microservices. We have provided a script to automate this process.

```bash
# Make sure scripts are executable
chmod +x script/setup_venvs.sh script/run_all.sh

# Set up all Python virtual environments and install dependencies
./script/setup_venvs.sh
```

### 2. Running the Backend Services

Once the environments are set up, you can start all the backend services simultaneously using the runner script:

```bash
# Start all microservices in the background
./script/run_all.sh
```
*(To stop the services, simply press `Ctrl+C` in the terminal where the script is running.)*

### 3. Frontend Setup

To run the user interface, you must start the frontend application separately using Node.js:

```bash
cd frontend/red-line-frontend
npm install
npm run dev
```

---

## Microservices Ports Configuration

The project is composed of several microservices. By running the `./script/run_all.sh` script, the services are automatically started on the following ports:

| Microservice | Port | Local URL |
|---|---|---|
| hallucination_attack | 5000 | http://127.0.0.1:5000 |
| jailbreak_attack | 5001 | http://127.0.0.1:5001 |
| judge_agent | 5002 | http://127.0.0.1:5002 |
| main_service | 5003 | http://127.0.0.1:5003 |
| PII_extraction_attack | 5004 | http://127.0.0.1:5004 |
| prompt_injection_attack | 5005 | http://127.0.0.1:5005 |
| realtime_data_service | 5006 | http://127.0.0.1:5006 |
| SAGA_orchestrator | 5007 | http://127.0.0.1:5007 |