import aiosqlite

DATABASE = "core.db"


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

async def init_db():

    async with aiosqlite.connect(DATABASE) as db:

        # WARNINGS
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # GUILD SETTINGS
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                log_channel INTEGER,
                welcome_channel INTEGER,
                welcome_enabled INTEGER DEFAULT 0
            )
        """)

        # APPLICATIONS
        await db.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                ign TEXT NOT NULL,
                age TEXT NOT NULL,
                experience TEXT NOT NULL,
                availability TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CLAN MEMBERS
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clan_members (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                rank TEXT DEFAULT 'Member',
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, user_id)
            )
        """)

        await db.commit()


# ============================================================
# WARNINGS
# ============================================================

async def add_warning(guild_id, user_id, moderator_id, reason):

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            INSERT INTO warnings
            (guild_id, user_id, moderator_id, reason)
            VALUES (?, ?, ?, ?)
            """,
            (guild_id, user_id, moderator_id, reason)
        )
        await db.commit()


async def get_warnings(guild_id, user_id):

    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            """
            SELECT moderator_id, reason, created_at
            FROM warnings
            WHERE guild_id = ? AND user_id = ?
            ORDER BY created_at DESC
            """,
            (guild_id, user_id)
        )

        return await cursor.fetchall()


async def clear_warnings(guild_id, user_id):

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            DELETE FROM warnings
            WHERE guild_id = ? AND user_id = ?
            """,
            (guild_id, user_id)
        )
        await db.commit()


# ============================================================
# APPLICATIONS
# ============================================================

async def create_application(
    guild_id,
    user_id,
    username,
    ign,
    age,
    experience,
    availability
):

    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            """
            INSERT INTO applications
            (
                guild_id,
                user_id,
                username,
                ign,
                age,
                experience,
                availability
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                guild_id,
                user_id,
                username,
                ign,
                age,
                experience,
                availability
            )
        )

        await db.commit()

        return cursor.lastrowid


async def get_pending_applications(guild_id):

    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            """
            SELECT
                id,
                user_id,
                username,
                ign,
                age,
                experience,
                availability,
                created_at
            FROM applications
            WHERE guild_id = ?
            AND status = 'pending'
            ORDER BY id DESC
            """,
            (guild_id,)
        )

        return await cursor.fetchall()


async def update_application_status(
    application_id,
    status
):

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            UPDATE applications
            SET status = ?
            WHERE id = ?
            """,
            (status, application_id)
        )

        await db.commit()


# ============================================================
# GUILD SETTINGS
# ============================================================

async def get_guild_settings(guild_id):

    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            """
            SELECT
                log_channel,
                welcome_channel,
                welcome_enabled
            FROM guild_settings
            WHERE guild_id = ?
            """,
            (guild_id,)
        )

        return await cursor.fetchone()


async def create_guild_settings(guild_id):

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO guild_settings
            (guild_id)
            VALUES (?)
            """,
            (guild_id,)
        )

        await db.commit()


async def update_log_channel(guild_id, channel_id):

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            INSERT INTO guild_settings
            (guild_id, log_channel)
            VALUES (?, ?)
            ON CONFLICT(guild_id)
            DO UPDATE SET
                log_channel = excluded.log_channel
            """,
            (guild_id, channel_id)
        )

        await db.commit()


async def update_welcome_channel(guild_id, channel_id):

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            INSERT INTO guild_settings
            (guild_id, welcome_channel)
            VALUES (?, ?)
            ON CONFLICT(guild_id)
            DO UPDATE SET
                welcome_channel = excluded.welcome_channel
            """,
            (guild_id, channel_id)
        )

        await db.commit()


async def set_welcome_enabled(guild_id, enabled):

    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            INSERT INTO guild_settings
            (guild_id, welcome_enabled)
            VALUES (?, ?)
            ON CONFLICT(guild_id)
            DO UPDATE SET
                welcome_enabled = excluded.welcome_enabled
            """,
            (guild_id, 1 if enabled else 0)
        )

        await db.commit()


# ============================================================
# CLAN MEMBERS
# ============================================================

async def get_clan_member(guild_id, user_id):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
                rank,
                xp,
                level,
                joined_at
            FROM clan_members
            WHERE guild_id = ?
            AND user_id = ?
            """,
            (guild_id, user_id)
        )

        return await cursor.fetchone()


async def create_clan_member(guild_id, user_id):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO clan_members
            (guild_id, user_id)
            VALUES (?, ?)
            """,
            (guild_id, user_id)
        )

        await db.commit()


async def set_clan_rank(
    guild_id,
    user_id,
    rank
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            INSERT INTO clan_members
            (guild_id, user_id, rank)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET
                rank = excluded.rank
            """,
            (
                guild_id,
                user_id,
                rank
            )
        )

        await db.commit()


async def add_xp(
    guild_id,
    user_id,
    amount
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO clan_members
            (guild_id, user_id)
            VALUES (?, ?)
            """,
            (guild_id, user_id)
        )

        await db.execute(
            """
            UPDATE clan_members
            SET xp = xp + ?
            WHERE guild_id = ?
            AND user_id = ?
            """,
            (
                amount,
                guild_id,
                user_id
            )
        )

        await db.commit()


async def set_level(
    guild_id,
    user_id,
    level
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE clan_members
            SET level = ?
            WHERE guild_id = ?
            AND user_id = ?
            """,
            (
                level,
                guild_id,
                user_id
            )
        )

        await db.commit()


async def get_leaderboard(
    guild_id,
    limit=10
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
                user_id,
                rank,
                xp,
                level
            FROM clan_members
            WHERE guild_id = ?
            ORDER BY xp DESC
            LIMIT ?
            """,
            (
                guild_id,
                limit
            )
        )

        return await cursor.fetchall()


async def get_clan_members(guild_id):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
                user_id,
                rank,
                xp,
                level,
                joined_at
            FROM clan_members
            WHERE guild_id = ?
            ORDER BY xp DESC
            """,
            (guild_id,)
        )

        return await cursor.fetchall()