import json
from typing import Dict, List
from datetime import datetime, UTC

import redis.asyncio as redis

from domain.entities.guild_request import GuildJoinRequest
from domain.repositories.cache_repo import CacheRepositoryBase

from services.converters.orm_to_domain import cache_to_domain

request_key = 'request:guild:{tag}:user:{user_id}'
ttl = 24 * 60 * 60

class RedisRepository(CacheRepositoryBase):
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    
    async def request_list_by_tag(self, tag: str):
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
    
    async def request_list_by_user_id(self, user_id: int):
        requests = []
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=request_key.format(tag='*', user_id=user_id))
            for key in keys:
                parts = key.decode('utf-8').split(':')
                requests.append(await self.get_request(parts[2], user_id))
            if cursor == 0:
                break
        return requests
    
    
    async def request_list_delete_by_user_id(self, user_id: int):
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=request_key.format(tag='*', user_id=user_id))
            for key in keys:
                await self.redis.delete(key)
            if cursor == 0:
                break
    
    
    async def request_list_delete_by_guild_tag(self, tag: str):
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=request_key.format(tag=tag, user_id='*'))
            for key in keys:
                await self.redis.delete(key)
            if cursor == 0:
                break
            
            
    async def get_request(self, tag: str, user_id: int):
        cache = await self.redis.get(request_key.format(tag=tag, user_id=user_id))
        req = json.loads(cache)
        req['tag'] = tag
        req['user_id'] = user_id
        return cache_to_domain(req)
    
    
    async def save(self, request: GuildJoinRequest):
        if not await self.check_request(request.guild_tag, request.user_id):
            await self.create(request)
        else:
            cache = await self.redis.get(request_key.format(tag=request.guild_tag, user_id=request.user_id))
            req = json.loads(cache)
            req['user_name'] = request.username
            await self.redis.set(
                name=request_key.format(tag=str(request.guild_tag), user_id=request.user_id),
                value=json.dumps(req).encode('utf-8'),   
                keepttl=True
            )
    
    
    async def create(self, request: GuildJoinRequest):
        request.created_at = datetime.now(UTC)
        value = {
            'created_at': request.created_at.isoformat() if request.created_at else datetime.now(UTC).isoformat(),
            'user_name': request.username
        }
        await self.redis.set(
            name=request_key.format(tag=str(request.guild_tag), user_id=request.user_id),
            value=json.dumps(value).encode('utf-8'),
            ex=ttl
        )
        
        request.status = 'pending'
        return request
    
    
    async def delete(self, tag: str, user_id: int):
        await self.redis.delete(request_key.format(tag=tag, user_id=user_id))
    
    
    async def check_request(self, tag: str, user_id: int):
        return await self.redis.get(request_key.format(tag=tag, user_id=user_id)) is not None