import redis.asyncio as redis
import os
import json
from typing import Optional, Dict, Any

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

async def get_cached_response(prompt_key: str) -> Optional[Dict[str, Any]]:
    """Retrieves cached LLM response if it exists."""
    try:
        cached_data = await redis_client.get(prompt_key)
        if cached_data:
            return json.loads(cached_data)
    except Exception:
        pass # Fail gracefully if cache is down
    return None

async def set_cached_response(prompt_key: str, response_data: Dict[str, Any], expire_seconds: int = 3600):
    """Caches the LLM response for a set duration."""
    try:
        await redis_client.setex(prompt_key, expire_seconds, json.dumps(response_data))
    except Exception:
        pass