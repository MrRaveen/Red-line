#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Get the root directory of the project (one level up from the script directory)
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

echo "Starting setup in project root: $ROOT_DIR"
cd "$ROOT_DIR"

# Find all directories containing a requirements.txt file
# We exclude any hidden directories like .venv or .git
find . -name "requirements.txt" -not -path "*/.*/*" | while read -r req_file; do
    # Get the directory containing the requirements.txt
    SERVICE_DIR=$(dirname "$req_file")
    
    echo "========================================================"
    echo "Setting up microservice in: $SERVICE_DIR"
    echo "========================================================"
    
    # Navigate to the service directory
    cd "$SERVICE_DIR"
    
    # Create the virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment (.venv)..."
        python3 -m venv .venv
    else
        echo "Virtual environment (.venv) already exists. Skipping creation."
    fi
    
    # Activate the virtual environment
    echo "Activating virtual environment..."
    source .venv/bin/activate
    
    # Install or update dependencies
    echo "Upgrading pip..."
    pip install --upgrade pip
    
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    
    # Deactivate the virtual environment
    echo "Deactivating virtual environment..."
    deactivate
    
    # Return to the root directory before the next iteration
    cd "$ROOT_DIR"
    echo -e "Finished setup for $SERVICE_DIR\n"
done

echo "========================================================"
echo "All virtual environments have been successfully set up!"
echo "========================================================"
