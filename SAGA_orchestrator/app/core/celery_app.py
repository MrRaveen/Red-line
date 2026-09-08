import os
from celery import Celery
from app.config import Config

# Initialize Celery app
celery_app = Celery(
    "saga_orchestrator",
    broker=Config.get_redis_url(),
    backend=Config.get_redis_url(),
    include=["app.core.entryPoint"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_default_queue="saga_orchestrator_queue",
    broker_transport_options={
        'max_connections': Config.REDIS_MAX_CONNECTIONS,
        'socket_timeout': Config.REDIS_SOCKET_TIMEOUT,
        'socket_connect_timeout': Config.REDIS_SOCKET_CONNECT_TIMEOUT,
    },
    redis_backend_transport_options={
        'max_connections': Config.REDIS_MAX_CONNECTIONS,
        'socket_timeout': Config.REDIS_SOCKET_TIMEOUT,
        'socket_connect_timeout': Config.REDIS_SOCKET_CONNECT_TIMEOUT,
    }
)
