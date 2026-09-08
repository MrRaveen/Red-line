import os
import sys

# Ensure the root directory is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.core.celery_app import celery_app
# Import tasks so they are registered with the worker
import app.core.entryPoint

if __name__ == '__main__':
    # On Windows, --pool=solo is often required for Celery to work properly
    # without raising ValueError related to prefork execution.
    celery_app.worker_main(['worker', '--loglevel=info', '--pool=solo'])
