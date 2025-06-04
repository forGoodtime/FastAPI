import redis.asyncio as redis
from config import settings

redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)