import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger

redis_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
        )
    return redis_client


async def check_redis_health() -> bool:
    try:
        client = await get_redis_client()
        pong = await client.ping()
        return pong is True
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return False
