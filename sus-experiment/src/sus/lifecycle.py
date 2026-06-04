import time
from sus.storage.redis_client import redis_client
from sus.tdlib_client import td_client
from sus.copy import system_messages
from sus.config import settings

async def burn(chat_id: int):
    conv_id = await redis_client.get_active_conv(chat_id)
    if conv_id:
        participants = await redis_client.get_conv_participants(conv_id)
        await redis_client.delete_conv(conv_id)
        for p_id in participants:
            await td_client.send_text(int(p_id), system_messages.SPACE_CLOSED)
    else:
        await redis_client.client.delete(f"user:{chat_id}:state")
        await redis_client.client.delete(f"user:{chat_id}:mask")
        await redis_client.client.srem("active_users", chat_id)
        await td_client.send_text(chat_id, "Your selections have been cleared. Send /start again if you'd like to rejoin with new selections.")

async def graduate(chat_id: int):
    conv_id = await redis_client.get_active_conv(chat_id)
    if not conv_id:
        await td_client.send_text(chat_id, "You are not in an active space.")
        return

    await redis_client.client.set(f"user:{chat_id}:reflecting", conv_id, ex=300)
    await td_client.send_text(chat_id, "This space is coming to a close. What's one word that reflects this interaction?")

async def handle_reflection(chat_id: int, word: str):
    conv_id = await redis_client.client.get(f"user:{chat_id}:reflecting")
    if not conv_id:
        return

    await redis_client.client.delete(f"user:{chat_id}:reflecting")
    await burn(chat_id)

async def silence(chat_id: int):
    state = await redis_client.get_user_state(chat_id)
    if state == "ACTIVE":
        await redis_client.set_user_state(chat_id, "SILENCED")
        await td_client.send_text(chat_id, "You are now silenced. You will not be included in the next cycle. Send /start to resume.")
    elif state == "SILENCED":
        await redis_client.set_user_state(chat_id, "ACTIVE")
        await td_client.send_text(chat_id, "You are back. You will be included in the next cycle.")

async def close_expired_conversations():
    convs = await redis_client.client.smembers("active_conversations")
    now = int(time.time())
    expiry_threshold = settings.expiry_hours * 3600

    for conv_id in convs:
        created_at = await redis_client.client.get(f"conv:{conv_id}:created_at")
        if not created_at or (now - int(created_at)) >= expiry_threshold:
            # Notify participants
            participants = await redis_client.get_conv_participants(conv_id)
            for p_id in participants:
                await td_client.send_text(int(p_id), system_messages.SPACE_EXPIRED)

            # Delete conversation
            await redis_client.delete_conv(conv_id)
