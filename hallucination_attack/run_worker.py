import os
import sys

# Ensure the root of the project is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("Starting Celery Worker for Hallucination Attack Service...")
    os.system("celery -A app.core.celery_app worker --loglevel=info --pool=solo")
