import asyncio
import structlog
from sus.tdlib_client import td_client
from sus.commands import route_message
from sus.storage.postgres_client import postgres_client
from sus.scheduler import setup_scheduler
from sus.config import settings

# Configure logging
structlog.configure()
logger = structlog.get_logger()

async def main():
    logger.info("Starting SUS experiment...")

    # Check kill switch
    if settings.sus_frozen:
        logger.warning("SUS is FROZEN. Exiting.")
        return

    # Initialize storage
    await postgres_client.init_db()

    # Setup commands
    td_client.add_message_handler(route_message)

    # Start scheduler
    setup_scheduler()

    # Start TDLib
    try:
        await td_client.start()
    except Exception as e:
        logger.error(f"Failed to start TDLib: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
