import requests
import json

SAGA_API_URL = "http://localhost:8001/api/v1/start-workflow"
TARGET_URL = "http://host.docker.internal:4003/api/generate"

def test_trigger_workflow():
    print("=" * 50)
    print("Testing /start-workflow Route for Jailbreak Attack")
    print("=" * 50)
    
    payload = {
        "userID": "test_user_123",
        "targetURL": TARGET_URL,
        "job_name": "Mock LLM Jailbreak Attack Test",
        "job_type": "jailbreak attack",
        "description": "Testing the SAGA pipeline end-to-end against the Mock LLM for Jailbreak",
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
