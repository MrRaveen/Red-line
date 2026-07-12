# vs code tasks to run all services and stop services (VS code native)
```
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start hallucination_attack",
            "type": "shell",
            "command": "source .venv/bin/activate && python run.py 5000 ; exec bash",
            "options": {
                "cwd": "${workspaceFolder}/hallucination_attack"
            },
            "presentation": {
                "panel": "new"
            }
        },
        {
            "label": "Start jailbreak_attack",
            "type": "shell",
            "command": "source .venv/bin/activate && python run.py 5001 ; exec bash",
            "options": {
                "cwd": "${workspaceFolder}/jailbreak_attack"
            },
            "presentation": {
                "panel": "new"
            }
        },
        {
            "label": "Start judge_agent",
            "type": "shell",
            "command": "source .venv/bin/activate && python run.py 5002 ; exec bash",
            "options": {
                "cwd": "${workspaceFolder}/judge_agent"
            },
            "presentation": {
                "panel": "new"
            }
        },
        {
            "label": "Start main_service",
            "type": "shell",
            "command": "source .venv/bin/activate && python run.py 5003 ; exec bash",
            "options": {
                "cwd": "${workspaceFolder}/main_service"
            },
            "presentation": {
                "panel": "new"
            }
        },
        {
            "label": "Start PII_extraction_attack",
            "type": "shell",
            "command": "source .venv/bin/activate && python run.py 5004 ; exec bash",
            "options": {
                "cwd": "${workspaceFolder}/PII_extraction_attack"
            },
            "presentation": {
                "panel": "new"
            }
        },
        {
            "label": "Start prompt_injection_attack",
            "type": "shell",
            "command": "source .venv/bin/activate && python run.py 5005 ; exec bash",
            "options": {
                "cwd": "${workspaceFolder}/prompt_injection_attack"
            },
            "presentation": {
                "panel": "new"
            }
        },
        {
            "label": "Start realtime_data_service",
            "type": "shell",
            "command": "source .venv/bin/activate && python run.py 5006 ; exec bash",
            "options": {
                "cwd": "${workspaceFolder}/realtime_data_service"
            },
            "presentation": {
                "panel": "new"
            }
        },
        {
            "label": "Start SAGA_orchestrator",
            "type": "shell",
            "command": "source .venv/bin/activate && python run.py 5007 ; exec bash",
            "options": {
                "cwd": "${workspaceFolder}/SAGA_orchestrator"
            },
            "presentation": {
                "panel": "new"
            }
        },
        {
            "label": "Run All Services",
            "dependsOn": [
                "Start hallucination_attack",
                "Start jailbreak_attack",
                "Start judge_agent",
                "Start main_service",
                "Start PII_extraction_attack",
                "Start prompt_injection_attack",
                "Start realtime_data_service",
                "Start SAGA_orchestrator"
            ],
            "dependsOrder": "parallel",
            "problemMatcher": []
        },
        {
            "label": "Stop All Services",
            "type": "shell",
            "command": "pkill -f 'python run.py' || echo 'No services running'",
            "presentation": {
                "panel": "shared",
                "reveal": "always"
            },
            "problemMatcher": []
        }
    ]
}
```