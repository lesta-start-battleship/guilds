from typing import Dict, List
from datetime import datetime, UTC

import redis.asyncio as redis

request_key = f'request:guild:{0}:user:{1}'
ttl = 24 * 60 * 60

class RedisRepository:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def get_requests(self, tag: str) -> List[Dict[str, str]]:
        requests = []
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=request_key.format(tag, '*'))
            for key in keys:
                parts = key.split(':')
                requests.append({
                    'user_id': parts[-1],
                    'create_at': await self.redis.get(key)
                })
            if cursor == 0:
                break
        return requests
        
    async def add_request(self, tag: str, user_id: int):
        await self.redis.set(key=request_key.format(tag, user_id), val=datetime.now(UTC).isoformat(), ex=ttl)
        
    async def remove_request(self, tag: str, user_id: int):
        await self.redis.delete(request_key.format(tag, user_id))
        
    async def check_request(self, tag: str, user_id: int):
        return await self.redis.get(request_key.format(tag, user_id)) is not None