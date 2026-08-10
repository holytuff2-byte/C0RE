import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

from database import (
    add_warning,
    get_warnings,
    clear_warnings
)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def embed(self, title, description, color=0x111111):
        return discord.Embed(
            title=f"⬢ C0RE | {title}",
            description=description,
            color=color
        )

    # =========================
    # BAN
    # =========================

    @app_commands.command(
        name="ban",
        description="Ban a member from the server."
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):

        if member == interaction.user:
            return await interaction.response.send_message(
                embed=self.embed(
                    "Ban",
                    "❌ You cannot ban yourself."
                ),
                ephemeral=True
            )

        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(
                embed=self.embed(
                    "Ban",
                    "❌ You cannot ban someone with an equal or higher role."
                ),
                ephemeral=True
            )

        try:
            await member.ban(reason=reason)

            await interaction.response.send_message(
                embed=self.embed(
                    "Member Banned",
                    f"**User:** {member.mention}\n"
                    f"**Reason:** {reason}\n"
                    f"**Moderator:** {interaction.user.mention}",
                    0xE74C3C
                )
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                embed=self.embed(
                    "Ban",
                    "❌ I don't have permission to ban this member."
                ),
                ephemeral=True
            )

    # =========================
    # KICK
    # =========================

    @app_commands.command(
        name="kick",
        description="Kick a member from the server."
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):

        if member == interaction.user:
            return await interaction.response.send_message(
                embed=self.embed(
                    "Kick",
                    "❌ You cannot kick yourself."
                ),
                ephemeral=True
            )

        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(
                embed=self.embed(
                    "Kick",
                    "❌ You cannot kick someone with an equal or higher role."
                ),
                ephemeral=True
            )

        try:
            await member.kick(reason=reason)

            await interaction.response.send_message(
                embed=self.embed(
                    "Member Kicked",
                    f"**User:** {member.mention}\n"
                    f"**Reason:** {reason}\n"
                    f"**Moderator:** {interaction.user.mention}",
                    0xE67E22
                )
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                embed=self.embed(
                    "Kick",
                    "❌ I don't have permission to kick this member."
                ),
                ephemeral=True
            )

    # =========================
    # TIMEOUT
    # =========================

    @app_commands.command(
        name="timeout",
        description="Timeout a member."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],
        reason: str = "No reason provided"
    ):

        if member == interaction.user:
            return await interaction.response.send_message(
                embed=self.embed(
                    "Timeout",
                    "❌ You cannot timeout yourself."
                ),
                ephemeral=True
            )

        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(
                embed=self.embed(
                    "Timeout",
                    "❌ You cannot timeout someone with an equal or higher role."
                ),
                ephemeral=True
            )

        try:
            duration = timedelta(minutes=minutes)

            await member.timeout(
                duration,
                reason=reason
            )

            await interaction.response.send_message(
                embed=self.embed(
                    "Member Timed Out",
                    f"**User:** {member.mention}\n"
                    f"**Duration:** `{minutes}` minutes\n"
                    f"**Reason:** {reason}\n"
                    f"**Moderator:** {interaction.user.mention}",
                    0xF1C40F
                )
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                embed=self.embed(
                    "Timeout",
                    "❌ I don't have permission to timeout this member."
                ),
                ephemeral=True
            )

    # =========================
    # WARN
    # =========================

    @app_commands.command(
        name="warn",
        description="Warn a member."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):

        await add_warning(
            interaction.guild.id,
            member.id,
            interaction.user.id,
            reason
        )

        warnings = await get_warnings(
            interaction.guild.id,
            member.id
        )

        await interaction.response.send_message(
            embed=self.embed(
                "Warning Issued",
                f"**User:** {member.mention}\n"
                f"**Reason:** {reason}\n"
                f"**Total warnings:** `{len(warnings)}`\n"
                f"**Moderator:** {interaction.user.mention}",
                0xF1C40F
            )
        )

    # =========================
    # WARNINGS
    # =========================

    @app_commands.command(
        name="warnings",
        description="View a member's warnings."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        warnings = await get_warnings(
            interaction.guild.id,
            member.id
        )

        if not warnings:
            return await interaction.response.send_message(
                embed=self.embed(
                    "Warnings",
                    f"{member.mention} has no warnings."
                ),
                ephemeral=True
            )

        lines = []

        for index, warning in enumerate(warnings, 1):
            moderator_id, reason, created_at = warning

            lines.append(
                f"**#{index}** — {reason}\n"
                f"Moderator: <@{moderator_id}>\n"
                f"Date: `{created_at}`"
            )

        await interaction.response.send_message(
            embed=self.embed(
                f"Warnings • {member}",
                "\n\n".join(lines),
                0xF1C40F
            )
        )

    # =========================
    # RESET WARNINGS
    # =========================

    @app_commands.command(
        name="resetwarnings",
        description="Reset all warnings for a member."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def resetwarnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        await clear_warnings(
            interaction.guild.id,
            member.id
        )

        await interaction.response.send_message(
            embed=self.embed(
                "Warnings Reset",
                f"All warnings for {member.mention} have been removed.",
                0x2ECC71
            )
        )

    # =========================
    # CLEAR
    # =========================

    @app_commands.command(
        name="clear",
        description="Delete messages from the current channel."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100]
    ):

        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(
            limit=amount
        )

        await interaction.followup.send(
            embed=self.embed(
                "Messages Cleared",
                f"Deleted `{len(deleted)}` messages.",
                0x2ECC71
            ),
            ephemeral=True
        )

    # =========================
    # LOCK
    # =========================

    @app_commands.command(
        name="lock",
        description="Lock the current channel."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(
        self,
        interaction: discord.Interaction
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.guild.default_role
        )

        overwrite.send_messages = False

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            embed=self.embed(
                "Channel Locked",
                "🔒 This channel has been locked.",
                0xE74C3C
            )
        )

    # =========================
    # UNLOCK
    # =========================

    @app_commands.command(
        name="unlock",
        description="Unlock the current channel."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(
        self,
        interaction: discord.Interaction
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.guild.default_role
        )

        overwrite.send_messages = None

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            embed=self.embed(
                "Channel Unlocked",
                "🔓 This channel has been unlocked.",
                0x2ECC71
            )
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))