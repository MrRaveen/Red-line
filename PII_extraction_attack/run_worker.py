import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("Starting Celery Worker for pii_extraction_attack...")
    os.system("celery -A app.core.celery_app worker --loglevel=info --pool=solo")
