import re
import time
from collections import defaultdict, deque

import discord
from discord import app_commands
from discord.ext import commands


class Security(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Message timestamps per user
        self.message_history = defaultdict(lambda: deque(maxlen=8))

        # Join timestamps per guild
        self.join_history = defaultdict(lambda: deque(maxlen=20))

        # Users allowed to bypass automatic message filtering
        self.whitelist = defaultdict(set)

        # Common scam / phishing patterns
        self.scam_patterns = [
            r"free\s+nitro",
            r"discord\s+nitro\s+free",
            r"claim\s+your\s+nitro",
            r"free\s+robux",
            r"free\s+vbucks",
            r"free\s+gift",
            r"steam\s+gift",
            r"airdrop",
            r"crypto\s+giveaway",
            r"verify\s+your\s+account",
            r"verify\s+now",
            r"login\s+to\s+claim",
            r"claim\s+reward",
            r"limited\s+time\s+offer",
        ]

        # Domains commonly abused in scam messages.
        self.blocked_domains = [
            "discord-gift",
            "discordnitro",
            "free-nitro",
            "nitro-free",
            "steamcommunity-gift",
            "roblox-gift",
        ]

    # =========================
    # HELPERS
    # =========================

    def is_whitelisted(self, guild_id, user_id):
        return user_id in self.whitelist[guild_id]

    def contains_scam(self, content):

        lowered = content.lower()

        for pattern in self.scam_patterns:
            if re.search(pattern, lowered):
                return True

        for domain in self.blocked_domains:
            if domain in lowered:
                return True

        return False

    def contains_link(self, content):

        pattern = r"https?://\S+|www\.\S+|discord\.gg/\S+"

        return bool(re.search(pattern, content.lower()))

    # =========================
    # MESSAGE SECURITY
    # =========================

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if not message.guild:
            return

        guild_id = message.guild.id
        user_id = message.author.id

        if self.is_whitelisted(guild_id, user_id):
            return

        now = time.monotonic()

        history = self.message_history[user_id]
        history.append(now)

        # -------------------------
        # ANTI-SPAM
        # -------------------------

        recent = [
            timestamp
            for timestamp in history
            if now - timestamp <= 6
        ]

        if len(recent) >= 6:

            try:
                await message.delete()
            except discord.HTTPException:
                pass

            try:
                await message.author.timeout(
                    discord.utils.utcnow()
                    + __import__("datetime").timedelta(
                        minutes=2
                    ),
                    reason="C0RE Anti-Spam"
                )
            except discord.HTTPException:
                pass

            try:
                await message.channel.send(
                    embed=discord.Embed(
                        title="⬢ C0RE | Anti-Spam",
                        description=(
                            f"{message.author.mention} was timed out "
                            "for excessive message spam."
                        ),
                        color=0xE74C3C
                    ),
                    delete_after=6
                )
            except discord.HTTPException:
                pass

            history.clear()

            return

        # -------------------------
        # SCAM DETECTION
        # -------------------------

        if self.contains_scam(message.content):

            try:
                await message.delete()
            except discord.HTTPException:
                pass

            try:
                await message.author.timeout(
                    discord.utils.utcnow()
                    + __import__("datetime").timedelta(
                        minutes=10
                    ),
                    reason="C0RE Anti-Scam"
                )
            except discord.HTTPException:
                pass

            try:
                await message.channel.send(
                    embed=discord.Embed(
                        title="⬢ C0RE | Security",
                        description=(
                            f"🚨 Suspicious content from "
                            f"{message.author.mention} was removed."
                        ),
                        color=0xE74C3C
                    ),
                    delete_after=8
                )
            except discord.HTTPException:
                pass

            return

        # -------------------------
        # INVITE / LINK FILTER
        # -------------------------

        if self.contains_link(message.content):

            # Only automatically remove obvious scam links.
            if self.contains_scam(message.content):

                try:
                    await message.delete()
                except discord.HTTPException:
                    pass

                return

        await self.bot.process_commands(message)

    # =========================
    # JOIN / RAID DETECTION
    # =========================

    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild_id = member.guild.id
        now = time.monotonic()

        history = self.join_history[guild_id]
        history.append(now)

        recent = [
            timestamp
            for timestamp in history
            if now - timestamp <= 30
        ]

        # 10+ joins within 30 seconds = possible raid.
        if len(recent) >= 10:

            try:
                await member.guild.system_channel.send(
                    embed=discord.Embed(
                        title="⬢ C0RE | RAID ALERT",
                        description=(
                            "🚨 **Possible raid detected.**\n\n"
                            f"`{len(recent)}` members joined within "
                            "the last 30 seconds.\n\n"
                            "Staff should review the server immediately."
                        ),
                        color=0xE74C3C
                    )
                )
            except discord.HTTPException:
                pass

            # Clear so the same raid doesn't spam alerts.
            history.clear()

    # =========================
    # WHITELIST
    # =========================

    @app_commands.command(
        name="whitelist",
        description="Whitelist a member from automatic security filtering."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def whitelist(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        guild_id = interaction.guild.id

        self.whitelist[guild_id].add(member.id)

        await interaction.response.send_message(
            embed=discord.Embed(
                title="⬢ C0RE | Whitelist",
                description=(
                    f"✅ {member.mention} has been added to "
                    "the security whitelist."
                ),
                color=0x2ECC71
            ),
            ephemeral=True
        )

    # =========================
    # UNWHITELIST
    # =========================

    @app_commands.command(
        name="unwhitelist",
        description="Remove a member from the security whitelist."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def unwhitelist(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        guild_id = interaction.guild.id

        self.whitelist[guild_id].discard(member.id)

        await interaction.response.send_message(
            embed=discord.Embed(
                title="⬢ C0RE | Whitelist",
                description=(
                    f"✅ {member.mention} has been removed from "
                    "the security whitelist."
                ),
                color=0x2ECC71
            ),
            ephemeral=True
        )

    # =========================
    # SECURITY STATUS
    # =========================

    @app_commands.command(
        name="security",
        description="View C0RE security status."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def security(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="⬢ C0RE | Security Status",
            description="Current automatic protection systems.",
            color=0x111111
        )

        embed.add_field(
            name="🛡️ Anti-Spam",
            value="`ACTIVE`",
            inline=True
        )

        embed.add_field(
            name="🔗 Scam Detection",
            value="`ACTIVE`",
            inline=True
        )

        embed.add_field(
            name="🚨 Raid Detection",
            value="`ACTIVE`",
            inline=True
        )

        embed.add_field(
            name="👤 Whitelist",
            value=f"`{len(self.whitelist[interaction.guild.id])}` users",
            inline=True
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Security(bot))