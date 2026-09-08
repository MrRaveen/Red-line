import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
dotenv_path = os.path.join(os.path.dirname(__file__), '../../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv()

class Config:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_TOPIC_SEND_PREPROCESSED = os.getenv("KAFKA_TOPIC_SEND_PREPROCESSED")
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB = os.getenv("MONGO_DB")
    MONGO_COLLECTION_TRANSACTIONS = "transaction_data"
    MONGO_COLLECTION_EXECUTION = "execution_logs"
    NODE_COMPLETE=os.getenv('NODE_COMPLETE')
    RESULTS_OUT=os.getenv('RESULTS_OUT')
