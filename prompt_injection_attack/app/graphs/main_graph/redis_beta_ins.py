import os
import redis

class RedisClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if RedisClient._client is None:
            RedisClient._client = self._create_client()

    @staticmethod
    def _create_client():
        # Parse integer env vars with defaults
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        db = int(os.getenv("REDIS_DB", 0))
        password = os.getenv("REDIS_PASSWORD") or None
        username = os.getenv("REDIS_USERNAME") or None
        max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", 50))
        socket_timeout = int(os.getenv("REDIS_SOCKET_TIMEOUT", 5))
        socket_connect_timeout = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", 5))

        pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            username=username,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            decode_responses=True,
        )
        return redis.Redis(connection_pool=pool)

    @property
    def client(self):
        return RedisClient._client

# Singleton instance
redis_client = RedisClient().client