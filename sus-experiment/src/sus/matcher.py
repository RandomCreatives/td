import random
import uuid
from sus.storage.redis_client import redis_client
from sus.intent_engine import get_overlap
from sus.tdlib_client import td_client
from sus.copy import system_messages
from sus.config import settings

async def run_matching_cycle():
    # 1. Get all active users
    # This is tricky with Redis without a full index.
    # For beta (<1000 users), we can maintain a set of active users.
    active_users = await redis_client.client.smembers("active_users")

    eligible = []
    for user_id_str in active_users:
        user_id = int(user_id_str)
        state = await redis_client.get_user_state(user_id)
        if state == "ACTIVE":
            mask = await redis_client.get_user_mask(user_id)
            eligible.append((user_id, mask))

    if len(eligible) < 2:
        return

    # 2. Compute pairwise overlaps
    matches = []
    for i in range(len(eligible)):
        for j in range(i + 1, len(eligible)):
            u1, m1 = eligible[i]
            u2, m2 = eligible[j]
            overlap = get_overlap(m1, m2)
            if overlap >= settings.overlap_threshold:
                matches.append((u1, u2, overlap))

    # 3. Greedy selection
    matches.sort(key=lambda x: x[2], reverse=True)

    matched_today = set()
    for u1, u2, overlap in matches:
        if u1 in matched_today or u2 in matched_today:
            continue

        matched_today.add(u1)
        matched_today.add(u2)

        # Create bridge offer
        await create_bridge_offer(u1, u2, overlap)

async def create_bridge_offer(u1: int, u2: int, overlap: int):
    conv_id = str(uuid.uuid4())
    # State for pending offer
    offer_key = f"offer:{conv_id}"
    await redis_client.client.hset(offer_key, mapping={
        "u1": u1,
        "u2": u2,
        "u1_accepted": 0,
        "u2_accepted": 0
    })
    await redis_client.client.expire(offer_key, 21600) # 6 hours

    # Store which conv is offered to which user
    await redis_client.client.set(f"user:{u1}:offered_conv", conv_id, ex=21600)
    await redis_client.client.set(f"user:{u2}:offered_conv", conv_id, ex=21600)

    await redis_client.set_user_state(u1, "OFFERED")
    await redis_client.set_user_state(u2, "OFFERED")

    msg = system_messages.BRIDGE_OFFER_SOUL if overlap >= 4 else system_messages.BRIDGE_OFFER_CURIOSITY
    await td_client.send_text(u1, msg)
    await td_client.send_text(u2, msg)

async def handle_offer_response(chat_id: int, text: str):
    conv_id = await redis_client.client.get(f"user:{chat_id}:offered_conv")
    if not conv_id:
        return

    offer_key = f"offer:{conv_id}"
    data = await redis_client.client.hgetall(offer_key)
    if not data:
        return

    u1 = int(data["u1"])
    u2 = int(data["u2"])

    if text.upper() == "YES":
        if chat_id == u1:
            await redis_client.client.hset(offer_key, "u1_accepted", 1)
        else:
            await redis_client.client.hset(offer_key, "u2_accepted", 1)

        # Check if both accepted
        updated_data = await redis_client.client.hgetall(offer_key)
        if updated_data.get("u1_accepted") == "1" and updated_data.get("u2_accepted") == "1":
            await start_conversation(conv_id, u1, u2)

    elif text.upper() == "NO":
        # Decline
        await redis_client.set_user_state(u1, "ACTIVE")
        await redis_client.set_user_state(u2, "ACTIVE")
        await redis_client.client.delete(f"user:{u1}:offered_conv")
        await redis_client.client.delete(f"user:{u2}:offered_conv")
        await redis_client.client.delete(offer_key)

async def start_conversation(conv_id: str, u1: int, u2: int):
    await redis_client.set_user_state(u1, "BRIDGED")
    await redis_client.set_user_state(u2, "BRIDGED")
    await redis_client.set_active_conv(u1, conv_id)
    await redis_client.set_active_conv(u2, conv_id)
    await redis_client.add_to_conv(conv_id, u1)
    await redis_client.add_to_conv(conv_id, u2)

    await td_client.send_text(u1, system_messages.SPACE_OPENED)
    await td_client.send_text(u2, system_messages.SPACE_OPENED)

    # Cleanup offer
    await redis_client.client.delete(f"user:{u1}:offered_conv")
    await redis_client.client.delete(f"user:{u2}:offered_conv")
    await redis_client.client.delete(f"offer:{conv_id}")
