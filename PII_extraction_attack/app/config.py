import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
    OLLAMA_MODEL_ID = os.getenv('OLLAMA_MODEL_ID')
    OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
    
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    PII_INJECT_IN_TOPIC = os.getenv("PII_INJECT_IN_TOPIC")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017")
