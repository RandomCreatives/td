import asyncpg
from sus.config import settings

class PostgresClient:
    def __init__(self):
        self.dsn = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.dsn)

    async def init_db(self):
        await self.connect()
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS consent_events (
                    id BIGSERIAL PRIMARY KEY,
                    anon_hash TEXT NOT NULL,
                    consent_version TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS intent_events (
                    id BIGSERIAL PRIMARY KEY,
                    anon_hash TEXT NOT NULL,
                    intent_mask INT NOT NULL,
                    quadrant_distribution JSONB NOT NULL,
                    taboo_score INT NOT NULL,
                    cycle_id INT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS match_events (
                    id BIGSERIAL PRIMARY KEY,
                    overlap_count INT NOT NULL,
                    shared_mask INT NOT NULL,
                    tier TEXT NOT NULL,
                    cycle_id INT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS conversation_outcomes (
                    id BIGSERIAL PRIMARY KEY,
                    match_event_id BIGINT,
                    duration_seconds INT NOT NULL,
                    message_count INT NOT NULL,
                    terminated_by TEXT NOT NULL,
                    graduation_word TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

    async def log_consent(self, anon_hash: str, version: str):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO consent_events (anon_hash, consent_version) VALUES (, )", anon_hash, version)

    async def log_intents(self, anon_hash: str, mask: int, distribution: str, taboo_score: int):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO intent_events (anon_hash, intent_mask, quadrant_distribution, taboo_score) VALUES (, , , )",
                               anon_hash, mask, distribution, taboo_score)

postgres_client = PostgresClient()
