from sus.storage.redis_client import redis_client
from sus.tdlib_client import td_client
from sus.copy import system_messages

async def burn(chat_id: int):
    conv_id = await redis_client.get_active_conv(chat_id)
    if conv_id:
        # Close space for both
        participants = await redis_client.get_conv_participants(conv_id)
        await redis_client.delete_conv(conv_id)
        for p_id in participants:
            await td_client.send_text(int(p_id), system_messages.SPACE_CLOSED)
    else:
        # Clear user state and mask
        await redis_client.client.delete(f"user:{chat_id}:state")
        await redis_client.client.delete(f"user:{chat_id}:mask")
        await redis_client.client.srem("active_users", chat_id)
        await td_client.send_text(chat_id, "Your selections have been cleared. Send /start again if you'd like to rejoin with new selections.")

async def graduate(chat_id: int):
    conv_id = await redis_client.get_active_conv(chat_id)
    if not conv_id:
        await td_client.send_text(chat_id, "You are not in an active space.")
        return

    # Soft exit with reflection
    await redis_client.client.set(f"user:{chat_id}:reflecting", conv_id, ex=300)
    await td_client.send_text(chat_id, "This space is coming to a close. What's one word that reflects this interaction?")

async def handle_reflection(chat_id: int, word: str):
    conv_id = await redis_client.client.get(f"user:{chat_id}:reflecting")
    if not conv_id:
        return

    # Log outcome
    # (Optional: In a real implementation, we'd calculate duration/msg count)
    # await postgres_client.log_outcome(...)

    await redis_client.client.delete(f"user:{chat_id}:reflecting")
    await burn(chat_id) # For now, graduate leads to a burn/reset of the space.

async def silence(chat_id: int):
    state = await redis_client.get_user_state(chat_id)
    if state == "ACTIVE":
        await redis_client.set_user_state(chat_id, "SILENCED")
        await td_client.send_text(chat_id, "You are now silenced. You will not be included in the next cycle. Send /start to resume.")
    elif state == "SILENCED":
        await redis_client.set_user_state(chat_id, "ACTIVE")
        await td_client.send_text(chat_id, "You are back. You will be included in the next cycle.")
