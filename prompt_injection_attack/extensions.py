import redis
from flask import current_app, g

#get a connection from the pool
def get_redis_pool(app):
    return redis.ConnectionPool(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=app.config["REDIS_DB"],
        username=app.config.get("REDIS_USERNAME"),
        password=app.config.get("REDIS_PASSWORD"),
        ssl=app.config["REDIS_SSL"],
        max_connections=app.config["REDIS_MAX_CONNECTIONS"],
        socket_timeout=app.config["REDIS_SOCKET_TIMEOUT"],
        socket_connect_timeout=app.config["REDIS_SOCKET_CONNECT_TIMEOUT"],
        decode_responses=True,
    )
#DB Con init phase - calls in the __init__.py file
def init_redis(app):
    app.redis_pool = get_redis_pool(app)

def get_redis():
    # g is Flask's global request context object
    # It's a thread-safe dictionary-like object that stores data for the duration of a single request

    # Lives only during a single HTTP request
    # Different for each request (thread-safe)
    # Automatically cleared when request ends
    # Perfect for caching database connections, clients, etc.
    if "redis_client" not in g:
        g.redis_client = redis.Redis(connection_pool=current_app.redis_pool)
    return g.redis_client