import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv()

class Config:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    PROMPT_INJECT_IN_TOPIC = os.getenv('PROMPT_INJECT_IN_TOPIC')
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
    OLLAMA_MODEL_ID = os.getenv('OLLAMA_MODEL_ID')
    OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
