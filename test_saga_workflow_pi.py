import requests
import json

# URL of the SAGA Orchestrator API (port 8001 as defined in docker-compose)
SAGA_API_URL = "http://localhost:8001/api/v1/start-workflow"

# The target URL for the attack.
# Since the mock LLM is running locally on the host machine at port 4000, 
# and the attack services are running inside Docker, we use host.docker.internal
# so the containers can reach the host. If your Docker setup doesn't support 
# host.docker.internal, you may need to use your machine's local IP address instead.
TARGET_URL = "http://host.docker.internal:4000/api/generate"

def test_trigger_workflow():
    print("=" * 50)
    print("Testing /start-workflow Route for Prompt Injection")
    print("=" * 50)
    
    # Payload adhering to the StartWorkflowRequest Pydantic model
    payload = {
        "userID": "test_user_123",
        "targetURL": TARGET_URL,
        "job_name": "Mock LLM Prompt Injection Test",
        "job_type": "prompt injection",
        "description": "Testing the SAGA pipeline end-to-end against the Mock LLM",
    }
    
    print(f"\n[1] Sending POST request to {SAGA_API_URL}")
    print(f"Payload sent:\n{json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(SAGA_API_URL, json=payload)
        print(f"\n[2] Response Status Code: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"Response Body:\n{json.dumps(json_response, indent=2)}")
            
            if response.status_code == 202:
                print("\n[SUCCESS] The workflow was successfully queued!")
                print(f"Task ID: {json_response.get('task_id')}")
            else:
                print("\n[WARNING] Received unexpected status code.")
                
        except requests.exceptions.JSONDecodeError:
            print(f"Response Text (Not JSON):\n{response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n[!] ERROR: Failed to connect to {SAGA_API_URL}.")
        print("Please ensure the SAGA orchestrator is running (e.g., via 'docker compose up').")

if __name__ == "__main__":
    test_trigger_workflow()
