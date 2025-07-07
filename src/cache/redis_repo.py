import json
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
                requests.append(await self.get_request(tag, parts[-1]))
            if cursor == 0:
                break
        return requests
    
    async def get_request(self, tag: str, user_id: int) -> Dict[str, str]:
        raw_value = await self.redis.get(request_key.format(tag=tag, user_id=user_id))
        value = json.loads(raw_value)
        return {
            'user_id': user_id,
            'user_name': value['user_name'],
            'created_at': value['created_at']
        }
    
    async def add_request(self, tag: str, user_id: int, user_name):
        value = {'created_at': datetime.now(UTC).isoformat(), 'user_name': user_name}
        await self.redis.set(
            name=request_key.format(tag=tag, user_id=user_id),
            value=json.dumps(value).encode('utf-8'),
            ex=ttl
        )
    
    async def remove_request(self, tag: str, user_id: int):
        await self.redis.delete(request_key.format(tag=tag, user_id=user_id))
    
    async def check_request(self, tag: str, user_id: int):
        check = await self.redis.get(request_key.format(tag=tag, user_id=user_id))
        return check is not None