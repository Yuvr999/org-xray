import time
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException, status
from app.core.config import settings
from app.core.logging import logger
from app.services.redis import get_redis_client


class RateLimiter:
    """
    Sliding window / token rate limiter with Redis support and in-memory fallback.
    """

    def __init__(self, default_limit: int = 120, window_seconds: int = 60):
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        # In-memory storage for fallback: key -> list of timestamps
        self._memory_cache: Dict[str, list] = {}

    def _get_client_identifier(self, request: Request) -> str:
        # Check for user ID in state (if authenticated) or fallback to client IP
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"
        
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        elif request.client:
            ip = request.client.host
        else:
            ip = "unknown"
            
        return f"ip:{ip}"

    async def is_rate_limited(
        self,
        request: Request,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        key_prefix: str = "rate_limit"
    ) -> Tuple[bool, int, int]:
        """
        Check if request exceeds rate limit.
        Returns: (is_limited, remaining_requests, retry_after_seconds)
        """
        max_requests = limit or self.default_limit
        window_sec = window or self.window_seconds
        
        client_id = self._get_client_identifier(request)
        key = f"{key_prefix}:{client_id}"
        now = time.time()
        
        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            try:
                # Use Redis sorted set for sliding window
                pipe = redis_client.pipeline()
                # Remove timestamps older than window
                pipe.zremrangebyscore(key, 0, now - window_sec)
                # Add current request
                pipe.zadd(key, {str(now): now})
                # Count items in window
                pipe.zcard(key)
                # Set TTL
                pipe.expire(key, window_sec)
                results = await pipe.execute()
                
                request_count = results[2]
                remaining = max(0, max_requests - request_count)
                
                if request_count > max_requests:
                    return True, 0, window_sec
                return False, remaining, 0
            except Exception as e:
                logger.warning(f"Redis rate limiter failed, falling back to in-memory: {e}")

        # In-memory fallback
        timestamps = self._memory_cache.get(key, [])
        # Prune old timestamps
        cutoff = now - window_sec
        timestamps = [ts for ts in timestamps if ts > cutoff]
        
        if len(timestamps) >= max_requests:
            oldest = timestamps[0] if timestamps else now
            retry_after = max(1, int(window_sec - (now - oldest)))
            self._memory_cache[key] = timestamps
            return True, 0, retry_after
        
        timestamps.append(now)
        self._memory_cache[key] = timestamps
        remaining = max_requests - len(timestamps)
        return False, remaining, 0

    async def check(
        self,
        request: Request,
        limit: Optional[int] = None,
        window: Optional[int] = None,
        key_prefix: str = "rate_limit"
    ):
        """
        Dependency helper that raises 429 Too Many Requests if rate limit is exceeded.
        """
        limited, remaining, retry_after = await self.is_rate_limited(
            request, limit=limit, window=window, key_prefix=key_prefix
        )
        if limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )


rate_limiter = RateLimiter(default_limit=120, window_seconds=60)
sensitive_rate_limiter = RateLimiter(default_limit=30, window_seconds=60)
