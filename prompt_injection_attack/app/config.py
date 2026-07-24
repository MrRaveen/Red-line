import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv()

class Config:
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT") or 6379)
    REDIS_DB = int(os.environ.get("REDIS_DB") or 0)
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
    REDIS_USERNAME = os.environ.get("REDIS_USERNAME") or None
    REDIS_SSL = os.environ.get("REDIS_SSL", "false").lower() == "true"

    REDIS_MAX_CONNECTIONS = int(os.environ.get("REDIS_MAX_CONNECTIONS") or 50)
    REDIS_SOCKET_TIMEOUT = 5
    REDIS_SOCKET_CONNECT_TIMEOUT = 5
