import redis
import json
import hashlib
from app.core.config import settings

redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

def get_cache_key(question: str, user_id: int) -> str:
    content = f"{user_id}:{question.lower().strip()}"
    return f"agent:answer:{hashlib.md5(content.encode()).hexdigest()}"

def get_cached_answer(question: str, user_id: int) -> dict | None:
    try:
        key = get_cache_key(question, user_id)
        cached = redis_client.get(key)
        if cached:
            print(f"[Redis] Cache HIT for: {question[:50]}")
            return json.loads(cached)
        print(f"[Redis] Cache MISS for: {question[:50]}")
        return None
    except Exception as e:
        print(f"[Redis] Cache get error: {e}")
        return None

def set_cached_answer(question: str, user_id: int, answer: dict, ttl: int = 3600):
    try:
        key = get_cache_key(question, user_id)
        redis_client.setex(key, ttl, json.dumps(answer))
        print(f"[Redis] Cached answer for: {question[:50]}")
    except Exception as e:
        print(f"[Redis] Cache set error: {e}")