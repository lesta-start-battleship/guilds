from .redis_repo_ import RedisRepository
from settings import settings

redis = RedisRepository(settings.redis_url)