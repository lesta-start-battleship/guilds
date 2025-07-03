from src.services.redis_service import RedisRepository
from src.settings import settings

redis = RedisRepository(settings.redis_url)