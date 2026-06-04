from aiotdlib.api import Message, MessageText
from sus.storage.redis_client import redis_client
from sus.onboarding import start_onboarding, handle_onboarding
from sus.matcher import handle_offer_response
from sus.relay import handle_relay
from sus.safety import handle_report, confirm_report
from sus.lifecycle import burn, graduate, silence, handle_reflection
from sus.tdlib_client import td_client

async def route_message(message: Message):
    chat_id = message.chat_id
    if not isinstance(message.content, MessageText):
        # We handle media blocking in relay for bridged users,
        # for others we can just ignore or notify.
        conv_id = await redis_client.get_active_conv(chat_id)
        if conv_id:
            from sus.relay import handle_relay
            await handle_relay(message, conv_id)
        return

    text = message.content.text.text.strip()
    state = await redis_client.get_user_state(chat_id)

    # Universal Commands
    if text == "/start":
        await start_onboarding(chat_id)
        return
    elif text == "/burn":
        await burn(chat_id)
        return
    elif text == "/help":
        await td_client.send_text(chat_id, "Available commands: /start, /burn, /help. During a space: /report, /graduate.")
        return

    # State-based Routing
    if not state:
        await td_client.send_text(chat_id, "Send /start to begin.")
        return

    if state in ["AGE_GATE", "CONSENT", "INTENT_SELECTION"]:
        await handle_onboarding(chat_id, text, state)
    elif state == "OFFERED":
        await handle_offer_response(chat_id, text)
    elif state == "BRIDGED":
        if text == "/report":
            await handle_report(chat_id)
        elif text == "/graduate":
            await graduate(chat_id)
        else:
            # Check if confirming report or reflecting
            is_reporting = await redis_client.client.get(f"user:{chat_id}:reporting")
            if is_reporting:
                await confirm_report(chat_id, text)
            else:
                is_reflecting = await redis_client.client.get(f"user:{chat_id}:reflecting")
                if is_reflecting:
                    await handle_reflection(chat_id, text)
                else:
                    conv_id = await redis_client.get_active_conv(chat_id)
                    await handle_relay(message, conv_id)
    elif state == "ACTIVE":
        if text == "/silence":
            await silence(chat_id)
        else:
            await td_client.send_text(chat_id, "There's nothing to talk to yet. You're in the waiting cycle based on your selections. You'll be notified only if there's meaningful overlap.")
    elif state == "SILENCED":
        if text == "/start":
            await silence(chat_id) # Resumes
    elif state == "BANNED":
        # Silent failure for banned users
        pass
