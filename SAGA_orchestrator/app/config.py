from datetime import timedelta
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
    MONGO_URI = os.getenv("MONGO_URI")
    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
    
    # Cast string values from .env to integer seconds wrapped in timedelta
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 900))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 86400))
    )

    if MONGO_URI:
        if "/?" in MONGO_URI:
            MONGO_URI = MONGO_URI.replace("/?", "/redline_logs?")
        elif "?" in MONGO_URI:
            MONGO_URI = MONGO_URI.replace("?", "/redline_logs?")
        elif not MONGO_URI.endswith("/"):
            MONGO_URI += "/redline_logs"
        else:
            MONGO_URI += "redline_logs"

    MONGODB_SETTINGS = {
        'host': MONGO_URI
    }
    @staticmethod
    def get_redis_url():
        return f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}"
