import redis.asyncio as Redis

from src.settings import settings

redis = Redis.from_url(settings.redis_url)
    