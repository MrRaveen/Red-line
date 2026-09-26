from common.redis_instance import get_redis_ins
import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv()

class Config:
    RESULTS_OUT=os.getenv('RESULTS_OUT')
    # KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    # RESULTS_OUT=os.getenv('RESULTS_OUT')
    # REDIS_HOST=os.getenv('REDIS_HOST')
    REDIS_PORT=os.getenv('REDIS_PORT')
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
    OLLAMA_MODEL_ID = os.getenv('OLLAMA_MODEL_ID')
    OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
    REDIS_PUBSUB_PART=os.getenv('REDIS_PUBSUB_PART')
    REDIS_HOST="127.0.0.1"
    REDIS_PORT=6379
    r = get_redis_ins(host=REDIS_HOST,port=REDIS_PORT)

    KAFKA_BOOTSTRAP_SERVERS="127.0.0.1:9092"
