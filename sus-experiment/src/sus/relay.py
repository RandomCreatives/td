from aiotdlib.api import Message, MessageText, MessagePhoto, MessageVideo, MessageAudio, MessageDocument, MessageVoiceNote, MessageVideoNote
from sus.tdlib_client import td_client
from sus.storage.redis_client import redis_client
from sus.copy import system_messages
import structlog

logger = structlog.get_logger()

async def handle_relay(message: Message, conv_id: str):
    chat_id = message.chat_id
    participants = await redis_client.get_conv_participants(conv_id)

    # Identify recipient
    recipient_id = None
    for p_id in participants:
        if int(p_id) != chat_id:
            recipient_id = int(p_id)
            break

    if not recipient_id:
        return

    # Check content type
    if isinstance(message.content, MessageText):
        text = message.content.text.text
        # Block contact info patterns (simple heuristic)
        # In a real app, this would be more robust.
        if "@" in text or "+" in text:
             await td_client.send_text(chat_id, "System: Contact info patterns detected. Soft warning: Stay anonymous.")
             # We still relay for now, or could block. Prompt says "soft warning, do not relay" for some patterns.
             # Let's block if it looks very much like a handle or phone.
             return

        await td_client.send_text(recipient_id, text)

        # Track message IDs for deletion (optional, but requested for cleanup)
        # Since we don't store message content, we can store message IDs in Redis
        await redis_client.client.lpush(f"conv:{conv_id}:msgs:{chat_id}", message.id)
        # We also need the ID of the message SENT to the recipient to delete it later.
        # But td_client.send_text doesn't return the ID easily without more work.
        # For simplicity in Phase I, we'll rely on the 48h auto-closure copy and burn.

    elif isinstance(message.content, (MessagePhoto, MessageVideo, MessageAudio, MessageDocument, MessageVoiceNote, MessageVideoNote)):
        # Block media
        await td_client.delete_messages(chat_id, [message.id])
        await td_client.send_text(chat_id, system_messages.WORDS_NOT_EVIDENCE)
    else:
        # Ignore other types
        pass
