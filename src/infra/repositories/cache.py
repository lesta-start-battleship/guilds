from redis import Redis

request_key = f'request:guild:{0}:user:{1}'
ttl = 24 * 60 * 60

class RedisRepository:
    def _init__(self, redis: Redis):
        self.redis = redis

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