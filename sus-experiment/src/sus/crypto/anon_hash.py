import hmac
import hashlib
import secrets
from sus.storage.redis_client import redis_client

async def get_or_create_salt() -> bytes:
    salt_hex = await redis_client.get_current_salt()
    if not salt_hex:
        salt = secrets.token_bytes(32)
        await redis_client.set_current_salt(salt.hex())
        return salt
    return bytes.fromhex(salt_hex)

async def anon_hash(tg_user_id: int) -> str:
    salt = await get_or_create_salt()
    return hmac.new(salt, str(tg_user_id).encode(), hashlib.sha256).hexdigest()

async def rotate_salt():
    new_salt = secrets.token_bytes(32)
    await redis_client.set_current_salt(new_salt.hex())
    # Note: Old salt is overwritten in Redis, effectively destroying it as per requirements.
