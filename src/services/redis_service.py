import redis.asyncio as redis

invite_key = f'invite:user:{0}:guld:{1}'
request_key = f'request:guild:{0}:user:{1}'
ttl = 24 * 60 * 60

class RedisRepository:
    def _init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        
    # async def get_invites(self, user_id: int):
    #     invites = []
    #     while True:
    #         cursor, keys = self.redis.scan(cursor=cursor, match=invite_key.format(user_id, '*'))
    #         for key in keys:
    #             parts = key.split(':')
    #             invites.append(parts[-1])
    #         if cursor == 0:
    #             break
    #     return invites
    
    # async def add_invite(self, guild_id: int, user_id: int):
    #     await self.redis.set(key=invite_key.format(user_id, guild_id), val='1', ex=ttl)
        
    # async def remove_invite(self, guild_id: int, user_id: int):
    #     await self.redis.delete(invite_key.format(user_id, guild_id))
        
    # async def check_invite(self, guild_id: int, user_id: int):
    #     return self.redis.get(invite_key.format(user_id, guild_id)) is not None

    async def get_requests(self, guild_id: int):
        requests = []
        while True:
            cursor, keys = self.redis.scan(cursor=cursor, match=request_key.format(guild_id, '*'))
            for key in keys:
                parts = key.split(':')
                requests.append(parts[-1])
            if cursor == 0:
                break
        return requests
        
    async def add_request(self, guild_id: int, user_id: int):
        await self.redis.set(key=request_key.format(guild_id, user_id), val='1', ex=ttl)
        
    async def remove_request(self, guild_id: int, user_id: int):
        await self.redis.delete(request_key.format(guild_id, user_id))
        
    async def check_request(self, guild_id: int, user_id: int):
        return self.redis.get(request_key.format(guild_id, user_id)) is not None