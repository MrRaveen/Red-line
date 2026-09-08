import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_DB = os.getenv("REDIS_DB", "0")
    REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
    REDIS_SOCKET_TIMEOUT = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    REDIS_SOCKET_CONNECT_TIMEOUT = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))

    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    RESULTS_OUT = os.getenv("RESULTS_OUT", "results_out")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017")

    @staticmethod
    def get_redis_url():
        return f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}"
