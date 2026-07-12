#!/bin/bash

# Get the root directory of the project
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

# Array to store background process IDs
declare -a PIDS

# Cleanup function to kill all background processes when the script stops
cleanup() {
    echo -e "\nStopping all microservices..."
    for pid in "${PIDS[@]}"; do
        # Check if process is still running, then kill
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "Stopped process $pid"
        fi
    done
    echo "All services stopped."
    exit 0
}

# Catch Ctrl+C (SIGINT) and termination signals to run the cleanup function
trap cleanup SIGINT SIGTERM

# Base port number
PORT=5000

echo "========================================================"
echo "Starting all microservices..."
echo "========================================================"

# Find all microservice directories (directories with requirements.txt) and sort them alphabetically
SERVICES=$(find . -name "requirements.txt" -not -path "*/.*/*" -exec dirname {} \; | sort)

for SERVICE_DIR in $SERVICES; do
    cd "$SERVICE_DIR"
    
    if [ -d ".venv" ]; then
        # Activate the virtual environment
        source .venv/bin/activate
        
        echo "--> Starting $SERVICE_DIR on http://127.0.0.1:$PORT"
        
        # Start the application using run.py in the background, bound to a specific port
        python run.py $PORT &
        
        # Store the process ID of the last background command
        PID=$!
        PIDS+=($PID)
        
        # Deactivate the virtual environment
        deactivate
        
        # Increment the port for the next service
        ((PORT++))
    else
        echo "--> WARNING: No .venv found in $SERVICE_DIR. Please run script/setup_venvs.sh first."
    fi
    
    cd "$ROOT_DIR"
done

echo "========================================================"
echo "All microservices are running in the background."
echo "Press Ctrl+C to stop all services."
echo "========================================================"

# Wait for all background processes to finish
# (In practice, this waits indefinitely until the user presses Ctrl+C)
wait
