import redis.asyncio as redis
from sus.config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True
        )

    async def get_user_state(self, tg_user_id: int) -> str:
        return await self.client.get(f"user:{tg_user_id}:state")

    async def set_user_state(self, tg_user_id: int, state: str, ttl: int = 2592000): # 30 days
        await self.client.set(f"user:{tg_user_id}:state", state, ex=ttl)

    async def get_user_mask(self, tg_user_id: int) -> int:
        mask = await self.client.get(f"user:{tg_user_id}:mask")
        return int(mask) if mask else 0

    async def set_user_mask(self, tg_user_id: int, mask: int, ttl: int = 2592000):
        await self.client.set(f"user:{tg_user_id}:mask", mask, ex=ttl)

    async def get_active_conv(self, tg_user_id: int) -> str:
        return await self.client.get(f"user:{tg_user_id}:active_conv")

    async def set_active_conv(self, tg_user_id: int, conv_id: str, ttl: int = 172800): # 48 hours
        await self.client.set(f"user:{tg_user_id}:active_conv", conv_id, ex=ttl)

    async def clear_active_conv(self, tg_user_id: int):
        await self.client.delete(f"user:{tg_user_id}:active_conv")

    async def add_to_conv(self, conv_id: str, tg_user_id: int, ttl: int = 172800):
        key = f"conv:{conv_id}:participants"
        await self.client.sadd(key, tg_user_id)
        await self.client.expire(key, ttl)

    async def get_conv_participants(self, conv_id: str) -> list:
        return await self.client.smembers(f"conv:{conv_id}:participants")

    async def delete_conv(self, conv_id: str):
        participants = await self.get_conv_participants(conv_id)
        for p_id in participants:
            await self.clear_active_conv(int(p_id))
            await self.set_user_state(int(p_id), "active")
        await self.client.delete(f"conv:{conv_id}:participants")
        await self.client.delete(f"conv:{conv_id}:created_at")

    async def get_current_salt(self) -> str:
        return await self.client.get("salt:current")

    async def set_current_salt(self, salt: str, ttl: int = 604800): # 7 days
        await self.client.set("salt:current", salt, ex=ttl)

redis_client = RedisClient()
