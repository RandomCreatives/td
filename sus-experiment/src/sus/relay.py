import re
from aiotdlib.api import Message, MessageText, MessagePhoto, MessageVideo, MessageAudio, MessageDocument, MessageVoiceNote, MessageVideoNote
from sus.tdlib_client import td_client
from sus.storage.redis_client import redis_client
from sus.copy import system_messages
import structlog

logger = structlog.get_logger()

# Heuristic for contact info: usernames (@handle), phone numbers, links
CONTACT_INFO_PATTERN = re.compile(
    r'(?:@\w+)|'                                 # Username
    r'(?:\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})|' # Phone
    r'(?:https?://\S+)|(?:www\.\S+)',            # Links
    re.IGNORECASE
)

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

    # Track incoming message for cleanup
    await redis_client.client.lpush(f"conv:{conv_id}:msgs:{chat_id}", message.id)

    # Check content type
    if isinstance(message.content, MessageText):
        text = message.content.text.text

        # Filter contact info
        if CONTACT_INFO_PATTERN.search(text):
             await td_client.send_text(chat_id, "System: Contact info or links detected. Soft warning: Stay anonymous.")
             # Block relaying suspicious patterns
             return

        # Forward message
        sent_msg = await td_client.send_text(recipient_id, text)

        # Track the sent message ID in the recipient's cleanup list
        if sent_msg:
            await redis_client.client.lpush(f"conv:{conv_id}:msgs:{recipient_id}", sent_msg.id)

    elif isinstance(message.content, (MessagePhoto, MessageVideo, MessageAudio, MessageDocument, MessageVoiceNote, MessageVideoNote)):
        # Block media
        await td_client.delete_messages(chat_id, [message.id])
        await td_client.send_text(chat_id, system_messages.WORDS_NOT_EVIDENCE)
    else:
        # Ignore other types
        pass
