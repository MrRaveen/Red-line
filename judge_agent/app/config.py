import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv()

class Config:
    #kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    JUDGE_IN_TOPIC = os.getenv("JUDGE_IN_TOPIC")
    KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "my-flask-group")
    JUDGE_OUT_TOPIC = os.getenv("JUDGE_OUT_TOPIC")
    #mongoDB for logs
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "redline_logs")
    MONGO_COLLECTION_TRANSACTIONS = "transaction_data"
    MONGO_COLLECTION_EXECUTION = "execution_logs"
    MONGO_COLLECTION_SUMMARIES = "summerriesAttacks"
    
    # Ollama and HuggingFace
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
    OLLAMA_MODEL_ID = os.getenv("OLLAMA_MODEL_ID")
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
    HF_TOKEN = os.getenv("HF_TOKEN")