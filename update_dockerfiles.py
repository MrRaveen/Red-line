import os

services = [
    "SAGA_orchestrator",
    "judge_agent",
    "PII_extraction_attack",
    "jailbreak_attack",
    "hallucination_attack",
    "prompt_injection_attack_new"
]

for svc in services:
    dockerfile_path = f"{svc}/Dockerfile"
    if os.path.exists(dockerfile_path):
        with open(dockerfile_path, "r") as f:
            content = f.read()
        
        # Replace the base image
        content = content.replace("FROM python:3.11-slim", "FROM redline-base:v1")
        
        with open(dockerfile_path, "w") as f:
            f.write(content)
        print(f"Updated {dockerfile_path}")
    else:
        print(f"Warning: {dockerfile_path} not found.")
