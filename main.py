import os
import asyncio
import discord
from discord.ext import commands

from database import init_db


# ============================================================
# CONFIG
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")

BOT_NAME = "C0RE"
BOT_VERSION = "1.0.0"


# ============================================================
# BOT
# ============================================================

class CORE(commands.Bot):

    def __init__(self):

        intents = discord.Intents.default()

        intents.guilds = True
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=">",
            intents=intents,
            help_command=None
        )

    # ========================================================
    # STARTUP
    # ========================================================

    async def setup_hook(self):

        print("Initializing C0RE database...")

        await init_db()

        extensions = [
            "moderation",
            "security",
            "utility",
            "recruitment",
            "clan",
            "tickets"
        ]

        print("Loading C0RE modules...")

        for extension in extensions:

            try:

                await self.load_extension(extension)

                print(
                    f"✅ Loaded: {extension}"
                )

            except Exception as error:

                print(
                    f"❌ Failed to load {extension}: "
                    f"{type(error).__name__}: {error}"
                )

        print("Syncing slash commands...")

        try:

            synced = await self.tree.sync()

            print(
                f"✅ Synced {len(synced)} slash commands."
            )

        except Exception as error:

            print(
                f"❌ Slash command sync failed: "
                f"{type(error).__name__}: {error}"
            )

    # ========================================================
    # READY
    # ========================================================

    async def on_ready(self):

        print()
        print("=" * 50)
        print(f"🔥 {BOT_NAME} IS ONLINE")
        print("=" * 50)
        print(f"Bot:     {self.user}")
        print(f"ID:      {self.user.id}")
        print(f"Version: {BOT_VERSION}")
        print(f"Servers: {len(self.guilds)}")
        print("=" * 50)
        print()

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"C0RE | /help"
            )
        )


# ============================================================
# RUN
# ============================================================

async def main():

    if not TOKEN:

        raise RuntimeError(
            "DISCORD_TOKEN environment variable is missing."
        )

    bot = CORE()

    try:

        await bot.start(TOKEN)

    finally:

        await bot.close()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print("C0RE stopped.")
