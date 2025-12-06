import redis.asyncio as redis
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_USERNAME

class RedisService:
    def __init__(self):
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.password = REDIS_PASSWORD
        self.username = REDIS_USERNAME

        if self.username and self.password:
            redis_url = f"redis://{self.username}:{self.password}@{self.host}:{self.port}"
        elif self.password:
            redis_url = f"redis://:{self.password}@{self.host}:{self.port}"
        else:
            redis_url = f"redis://{self.host}:{self.port}"

        self._redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str):
        return await self._redis.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        await self._redis.set(key, value)
        if expire:
            await self._redis.expire(key, expire)

    async def close(self):
        await self._redis.close()
