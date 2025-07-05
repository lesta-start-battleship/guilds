from typing import Dict, List
from datetime import datetime, UTC

import redis.asyncio as redis

request_key = 'request:guild:{tag}:user:{user_id}'
ttl = 24 * 60 * 60

class RedisRepository:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def get_requests(self, tag: str) -> List[Dict[str, str]]:
        requests = []
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=request_key.format(tag=tag, user_id='*'))
            for key in keys:
                parts = key.decode('utf-8').split(':')
                requests.append({
                    'user_id': parts[-1],
                    'created_at': await self.redis.get(key)
                })
            if cursor == 0:
                break
        return requests
        
    async def add_request(self, tag: str, user_id: int):
        await self.redis.set(name=request_key.format(tag=tag, user_id=user_id), value=datetime.now(UTC).isoformat(), ex=ttl)
        
    async def remove_request(self, tag: str, user_id: int):
        await self.redis.delete(request_key.format(tag=tag, user_id=user_id))
        
    async def check_request(self, tag: str, user_id: int):
        check = await self.redis.get(request_key.format(tag=tag, user_id=user_id))
        return check is not None