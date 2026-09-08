import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_SEND_PREPROCESSED = os.getenv("KAFKA_TOPIC_SEND_PREPROCESSED", "preprocessed_topic")
    KAFKA_TOPIC_GET_PREPROCESSED = os.getenv('KAFKA_TOPIC_GET_PREPROCESSED','preprocess_in')
    KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "my-flask-group")
    FLASK_PORT_KAFKA_SERVICE = int(os.getenv("FLASK_PORT_KAFKA_SERVICE", 5002))
    #mongoDB for logs
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "redline_logs")
    MONGO_COLLECTION_TRANSACTIONS = "transaction_data"
    MONGO_COLLECTION_EXECUTION = "execution_logs"
    #log processor micro service
    FLASK_PORT_LOG_PROCESSOR = int(os.getenv("FLASK_PORT_LOG_PROCESSOR", 5003))
    
    