from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sus.matcher import run_matching_cycle
from sus.crypto.anon_hash import rotate_salt
from sus.lifecycle import close_expired_conversations
from sus.config import settings
import structlog

logger = structlog.get_logger()

scheduler = AsyncIOScheduler()

def setup_scheduler():
    # Daily match cycle
    scheduler.add_job(
        run_matching_cycle,
        'cron',
        hour=settings.cycle_hour,
        minute=0,
        timezone='Africa/Addis_Ababa'
    )

    # Weekly salt rotation
    scheduler.add_job(
        rotate_salt,
        'interval',
        days=settings.salt_rotation_days
    )

    # Check for expired conversations every 15 minutes
    scheduler.add_job(
        close_expired_conversations,
        'interval',
        minutes=15
    )

    scheduler.start()
    logger.info("Scheduler started")
