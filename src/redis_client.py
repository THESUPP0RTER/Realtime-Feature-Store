import os
from redis import Redis
from typing import Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Global Redis client instance
_redis_client: Optional[Redis] = None


def get_redis_client() -> Redis:
    """Get or create Redis client connection"""
    global _redis_client

    if _redis_client is None:
        _redis_client = Redis.from_url(
            REDIS_URL,
            decode_responses=True,  # Automatically decode responses to strings
            socket_connect_timeout=5,
            socket_timeout=5,
        )

    return _redis_client


def close_redis_client():
    """Close Redis client connection"""
    global _redis_client

    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
