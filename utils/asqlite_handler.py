import asqlite
import time

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
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS warntable (
                    guildid INTEGER,
                    memberid INTEGER,
                    warnreason TEXT,
                    time INTEGER
                );
            """)
            await conn.commit()

    async def add_warning(self, guild_id, member_id, warn_reason):
        """Add a warning to the database."""
        current_time = int(time.time())  # Get current time as UNIX timestamp
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO warntable (guildid, memberid, warnreason, time) VALUES (?, ?, ?, ?)",
                               (guild_id, member_id, warn_reason, current_time))
            await conn.commit()

    async def fetch_warnings(self, guild_id, member_id):
        """Fetch all warnings for a specific member."""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM warntable WHERE guildid = ? AND memberid = ?",
                                     (guild_id, member_id))
                return await cursor.fetchall()

    # Include more methods as required for updating or deleting warnings.
