from cache.redis_repo import RedisRepository
from settings import settings

redis = RedisRepository(settings.redis_url)