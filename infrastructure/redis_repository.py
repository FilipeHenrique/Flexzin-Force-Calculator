import os
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()

class RedisRepository:
    def __init__(self):
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        password = os.getenv("REDIS_PASSWORD", None)

        redis_url = f"redis://{host}:{port}"
        if password:
            redis_url = f"redis://:{password}@{host}:{port}"

        self._redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str):
        return await self._redis.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        await self._redis.set(key, value)
        if expire:
            await self._redis.expire(key, expire)

    async def close(self):
        await self._redis.close()
