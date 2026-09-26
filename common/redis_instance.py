import redis

redisIns = None

def get_redis_ins(host: str, port: int):
    global redisIns
    if redisIns is None:
        redisIns = redis.Redis(host=host, port=port, decode_responses=True)
    return redisIns
