from sus.storage.redis_client import redis_client
from sus.tdlib_client import td_client
from sus.copy import system_messages

async def handle_report(chat_id: int):
    conv_id = await redis_client.get_active_conv(chat_id)
    if not conv_id:
        await td_client.send_text(chat_id, "You are not in an active space.")
        return

    await redis_client.client.set(f"user:{chat_id}:reporting", conv_id, ex=300)
    await td_client.send_text(chat_id, "Are you reporting the other person in this space? Reply YES to confirm. This will silently end the space.")

async def confirm_report(chat_id: int, text: str):
    if text.upper() == "YES":
        conv_id = await redis_client.client.get(f"user:{chat_id}:reporting")
        if not conv_id:
            return

        participants = await redis_client.get_conv_participants(conv_id)
        other_id = None
        for p_id in participants:
            if int(p_id) != chat_id:
                other_id = int(p_id)
                break

        # Shadow-ban the other person
        if other_id:
            await shadow_ban(other_id)

        # Silently end space
        await redis_client.delete_conv(conv_id)
        await td_client.send_text(chat_id, "This space has been ended.")
        if other_id:
             await td_client.send_text(other_id, "This space has been ended.")

        await redis_client.client.delete(f"user:{chat_id}:reporting")
    else:
        await redis_client.client.delete(f"user:{chat_id}:reporting")
        await td_client.send_text(chat_id, "Report cancelled.")

async def shadow_ban(user_id: int):
    await redis_client.set_user_state(user_id, "BANNED")
    # Log safety event
    # (Optional: Add to postgres_client if needed)

async def is_banned(user_id: int) -> bool:
    state = await redis_client.get_user_state(user_id)
    return state == "BANNED"
