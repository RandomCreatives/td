from sus.storage.redis_client import redis_client
from sus.storage.postgres_client import postgres_client
from sus.crypto.anon_hash import anon_hash
from sus.copy import system_messages
from sus.intents import INTENT_LIST
from sus.tdlib_client import td_client
import json

async def start_onboarding(chat_id: int):
    await redis_client.set_user_state(chat_id, "AGE_GATE")
    await redis_client.client.sadd("active_users", chat_id)
    await td_client.send_text(chat_id, system_messages.WELCOME)

async def handle_onboarding(chat_id: int, text: str, state: str):
    if state == "AGE_GATE":
        if text.upper() == "YES":
            await redis_client.set_user_state(chat_id, "CONSENT")
            await td_client.send_text(chat_id, system_messages.CONSENT_PROMPT)
        elif text.upper() == "NO":
            await td_client.send_text(chat_id, system_messages.AGE_REJECTED)
            await redis_client.client.delete(f"user:{chat_id}:state")
            await redis_client.client.srem("active_users", chat_id)
        else:
            await td_client.send_text(chat_id, "Please reply YES or NO.")

    elif state == "CONSENT":
        if text.upper() == "I AGREE":
            h = await anon_hash(chat_id)
            await postgres_client.log_consent(h, "1.0")
            await redis_client.set_user_state(chat_id, "INTENT_SELECTION")

            # Prepare intent list display
            intents_text = system_messages.INTENT_SELECTION_PROMPT
            for i, intent in enumerate(INTENT_LIST):
                intents_text += f"{i+1}. {intent.label}\n"

            await td_client.send_text(chat_id, intents_text)
        elif text.upper() == "CANCEL":
            await td_client.send_text(chat_id, system_messages.CONSENT_REJECTED)
            await redis_client.client.delete(f"user:{chat_id}:state")
            await redis_client.client.srem("active_users", chat_id)
        else:
            await td_client.send_text(chat_id, "Please reply I AGREE or CANCEL.")

    elif state == "INTENT_SELECTION":
        try:
            # Parse numbers
            parts = [p.strip() for p in text.replace(',', ' ').split()]
            indices = [int(p) - 1 for p in parts]

            if len(indices) != 5:
                raise ValueError("Exactly 5 required")

            if any(i < 0 or i >= 20 for i in indices):
                raise ValueError("Invalid index")

            # Create bitmask
            mask = 0
            for i in indices:
                mask |= (1 << i)

            await redis_client.set_user_mask(chat_id, mask)
            await redis_client.set_user_state(chat_id, "ACTIVE")

            # Log for research
            h = await anon_hash(chat_id)
            dist = {}
            taboo_score = 0
            for i in indices:
                intent = INTENT_LIST[i]
                dist[intent.quadrant] = dist.get(intent.quadrant, 0) + 1
                taboo_score += intent.taboo_index

            await postgres_client.log_intents(h, mask, json.dumps(dist), taboo_score)
            await td_client.send_text(chat_id, system_messages.SELECTION_CONFIRMED)

        except ValueError:
            await td_client.send_text(chat_id, system_messages.INVALID_SELECTION)
