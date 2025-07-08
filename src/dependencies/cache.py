from redis.asyncio import Redis

from infra.cache.redis_instance import redis
from infra.cache.redis_repo_ import RedisRepository

def get_cache_repository(session: Redis = redis):
    return RedisRepository(session)