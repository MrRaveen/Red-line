import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv()

class Config:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    PREPROCESSOR_IN_TOPIC = os.getenv('PREPROCESSOR_IN_TOPIC')
    PREPROCESSOR_OUT_TOPIC = os.getenv('PREPROCESSOR_OUT_TOPIC')
