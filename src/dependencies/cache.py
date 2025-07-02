from redis.asyncio import Redis

from src.infra.redis_instance import redis
from src.infra.repositories.cache import RedisRepository

def get_cache_repository(session: Redis = redis):
    return RedisRepository(session)