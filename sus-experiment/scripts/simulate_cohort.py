import asyncio
import random
from unittest.mock import AsyncMock, patch, MagicMock

# Mock Client before imports
import aiotdlib
aiotdlib.Client = MagicMock()
aiotdlib.ClientSettings = MagicMock()

from sus.intent_engine import encode_mask
from sus.matcher import run_matching_cycle
from sus.config import settings

async def simulate():
    print("Simulating cohort of 100 users...")

    # Generate 100 random masks
    users = []
    for i in range(100):
        indices = random.sample(range(20), 5)
        mask = encode_mask(indices)
        users.append((i, mask))

    # Mock Redis responses
    mock_redis = AsyncMock()
    mock_redis.smembers.return_value = [str(u[0]) for u in users]

    # Helper to return state/mask for each user
    user_data = {u[0]: {"state": "ACTIVE", "mask": u[1]} for u in users}

    async def get_state(uid):
        return user_data[uid]["state"]

    async def get_mask(uid):
        return user_data[uid]["mask"]

    # Mocking Redis hgetall/hset/etc if needed
    mock_redis.hset = AsyncMock()
    mock_redis.hgetall = AsyncMock()
    mock_redis.expire = AsyncMock()
    mock_redis.set = AsyncMock()

    with patch('sus.storage.redis_client.redis_client.client', mock_redis),          patch('sus.storage.redis_client.redis_client.get_user_state', side_effect=get_state),          patch('sus.storage.redis_client.redis_client.get_user_mask', side_effect=get_mask),          patch('sus.storage.redis_client.redis_client.set_user_state', AsyncMock()),          patch('sus.tdlib_client.td_client.send_text', AsyncMock()) as mock_send_text:

        await run_matching_cycle()

        # Check how many bridge offers were sent
        # Each offer sends 2 messages (one to each user)
        offer_count = mock_send_text.call_count // 2
        print(f"Matching cycle complete. Created {offer_count} bridge offers.")

        if offer_count > 0:
            print("SUCCESS: Matching logic is functional.")
        else:
            print(f"INFO: No matches found in this random cohort. (Threshold: {settings.overlap_threshold})")

if __name__ == "__main__":
    asyncio.run(simulate())
