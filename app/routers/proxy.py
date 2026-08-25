from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import hashlib

from app.services.provider_router import route_llm_request
from app.services.redis_cache import get_cached_response, set_cached_response

router = APIRouter(prefix="/v1", tags=["LLM Gateway Proxy"])

class ChatCompletionRequest(BaseModel):
    model: str = Field(default="gpt-3.5-turbo")
    messages: list[Dict[str, str]]
    temperature: Optional[float] = 0.7
    provider: Optional[str] = "openai"

@router.post("/chat/completions")
async def proxy_chat_completions(
    payload: ChatCompletionRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    """
    Unified chat completion endpoint with automatic caching and provider failover.
    """
    # 1. Generate cache key based on messages and model choice
    payload_str = str(payload.messages) + payload.model
    cache_key = "llm_cache:" + hashlib.sha256(payload_str.encode()).hexdigest()

    # 2. Check Redis Cache first
    cached_res = await get_cached_response(cache_key)
    if cached_res:
        cached_res["source"] = "cache"
        return cached_res

    # 3. Route through provider fallback sequence if not cached
    try:
        response = await route_llm_request(payload.dict(), provider=payload.provider)
        
        # 4. Save successful response to cache
        await set_cached_response(cache_key, response)
        response["source"] = "live_provider"
        
        return response
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))