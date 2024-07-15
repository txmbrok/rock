import asqlite
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.pool = None

    async def setup(self):
        """Setup the database connection pool."""
        self.pool = await asqlite.create_pool(self.db_path)
        # Ensure tables are created when setting up the database.
        await self.create_tables()

    async def create_tables(self):
        if self.pool is None:
            raise RuntimeError("Database connection pool is not set up.")
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS warntable (
                    warn_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guildid INTEGER,
                    memberid INTEGER,
                    issuerid INTEGER,
                    warnreason TEXT,
                    time INTEGER
                );
            """)
            await conn.commit()

    async def add_warning(self, guild_id, member_id, issuer_id, warn_reason):
        if self.pool is None:
            raise RuntimeError("Database connection pool is not set up.")
        current_time = int(datetime.now().timestamp())
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO warntable (guildid, memberid, issuerid, warnreason, time) VALUES (?, ?, ?, ?, ?)",
                               (guild_id, member_id, issuer_id, warn_reason, current_time))
            await conn.commit()

    async def fetch_warnings(self, guild_id, member_id):
        """Fetch all warnings for a specific member."""
        if self.pool is None:
            raise RuntimeError("Database connection pool is not set up.")
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT warn_id, issuerid, warnreason, time
                    FROM warntable 
                    WHERE guildid = ? AND memberid = ?
                    ORDER BY time DESC
                """, (guild_id, member_id))
                return await cursor.fetchall()

