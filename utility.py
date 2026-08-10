import discord
from discord import app_commands
from discord.ext import commands

from database import (
    get_guild_settings,
    create_guild_settings,
    update_log_channel,
    update_welcome_channel,
    set_welcome_enabled
)


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # EMBED
    # ========================================================

    def embed(self, title, description, color=0x111111):

        return discord.Embed(
            title=f"⬢ C0RE | {title}",
            description=description,
            color=color
        )

    # ========================================================
    # SET LOG CHANNEL
    # ========================================================

    @app_commands.command(
        name="setlogs",
        description="Set the C0RE moderation log channel."
    )
    @app_commands.checks.has_permissions(
        manage_guild=True
    )
    async def setlogs(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        await create_guild_settings(
            interaction.guild.id
        )

        await update_log_channel(
            interaction.guild.id,
            channel.id
        )

        await interaction.response.send_message(
            embed=self.embed(
                "Logging",
                f"✅ Log channel set to {channel.mention}.",
                0x2ECC71
            ),
            ephemeral=True
        )

    # ========================================================
    # SET WELCOME CHANNEL
    # ========================================================

    @app_commands.command(
        name="setwelcome",
        description="Set the C0RE welcome channel."
    )
    @app_commands.checks.has_permissions(
        manage_guild=True
    )
    async def setwelcome(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        await create_guild_settings(
            interaction.guild.id
        )

        await update_welcome_channel(
            interaction.guild.id,
            channel.id
        )

        await interaction.response.send_message(
            embed=self.embed(
                "Welcome",
                f"✅ Welcome channel set to {channel.mention}.",
                0x2ECC71
            ),
            ephemeral=True
        )

    # ========================================================
    # WELCOME ON
    # ========================================================

    @app_commands.command(
        name="welcome",
        description="Enable or disable C0RE welcome messages."
    )
    @app_commands.checks.has_permissions(
        manage_guild=True
    )
    @app_commands.describe(
        enabled="Whether welcome messages should be enabled."
    )
    async def welcome(
        self,
        interaction: discord.Interaction,
        enabled: bool
    ):

        await create_guild_settings(
            interaction.guild.id
        )

        await set_welcome_enabled(
            interaction.guild.id,
            enabled
        )

        status = "enabled" if enabled else "disabled"

        await interaction.response.send_message(
            embed=self.embed(
                "Welcome",
                f"✅ Welcome messages have been **{status}**.",
                0x2ECC71
            ),
            ephemeral=True
        )

    # ========================================================
    # MEMBER JOIN
    # ========================================================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ):

        settings = await get_guild_settings(
            member.guild.id
        )

        if not settings:
            return

        log_channel_id = settings[0]
        welcome_channel_id = settings[1]
        welcome_enabled = settings[2]

        # -------------------------
        # WELCOME MESSAGE
        # -------------------------

        if welcome_enabled and welcome_channel_id:

            channel = member.guild.get_channel(
                welcome_channel_id
            )

            if channel:

                embed = self.embed(
                    "Welcome to C0RE",
                    (
                        f"🔥 Welcome {member.mention}!\n\n"
                        f"You are now member **#{member.guild.member_count}** "
                        f"of **{member.guild.name}**.\n\n"
                        "Read the server rules and check out "
                        "the clan channels to get started."
                    ),
                    0x111111
                )

                embed.set_thumbnail(
                    url=member.display_avatar.url
                )

                await channel.send(
                    embed=embed
                )

        # -------------------------
        # JOIN LOG
        # -------------------------

        if log_channel_id:

            channel = member.guild.get_channel(
                log_channel_id
            )

            if channel:

                embed = self.embed(
                    "Member Joined",
                    (
                        f"**User:** {member.mention}\n"
                        f"**ID:** `{member.id}`\n"
                        f"**Account:** <t:{int(member.created_at.timestamp())}:R>"
                    ),
                    0x2ECC71
                )

                await channel.send(
                    embed=embed
                )

    # ========================================================
    # MEMBER LEAVE
    # ========================================================

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member: discord.Member
    ):

        settings = await get_guild_settings(
            member.guild.id
        )

        if not settings:
            return

        log_channel_id = settings[0]

        if not log_channel_id:
            return

        channel = member.guild.get_channel(
            log_channel_id
        )

        if not channel:
            return

        embed = self.embed(
            "Member Left",
            (
                f"**User:** {member}\n"
                f"**ID:** `{member.id}`"
            ),
            0xE74C3C
        )

        await channel.send(
            embed=embed
        )

    # ========================================================
    # MESSAGE DELETE
    # ========================================================

    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message: discord.Message
    ):

        if not message.guild:
            return

        if message.author.bot:
            return

        settings = await get_guild_settings(
            message.guild.id
        )

        if not settings:
            return

        log_channel_id = settings[0]

        if not log_channel_id:
            return

        channel = message.guild.get_channel(
            log_channel_id
        )

        if not channel:
            return

        content = message.content or "*No text content*"

        if len(content) > 1000:
            content = content[:1000] + "..."

        embed = self.embed(
            "Message Deleted",
            (
                f"**Author:** {message.author.mention}\n"
                f"**Channel:** {message.channel.mention}\n\n"
                f"**Content:**\n{content}"
            ),
            0xE74C3C
        )

        await channel.send(
            embed=embed
        )

    # ========================================================
    # MESSAGE EDIT
    # ========================================================

    @commands.Cog.listener()
    async def on_message_edit(
        self,
        before: discord.Message,
        after: discord.Message
    ):

        if not before.guild:
            return

        if before.author.bot:
            return

        if before.content == after.content:
            return

        settings = await get_guild_settings(
            before.guild.id
        )

        if not settings:
            return

        log_channel_id = settings[0]

        if not log_channel_id:
            return

        channel = before.guild.get_channel(
            log_channel_id
        )

        if not channel:
            return

        old = before.content or "*Empty*"
        new = after.content or "*Empty*"

        if len(old) > 700:
            old = old[:700] + "..."

        if len(new) > 700:
            new = new[:700] + "..."

        embed = self.embed(
            "Message Edited",
            (
                f"**Author:** {before.author.mention}\n"
                f"**Channel:** {before.channel.mention}\n\n"
                f"**Before:**\n{old}\n\n"
                f"**After:**\n{new}"
            ),
            0xF1C40F
        )

        await channel.send(
            embed=embed
        )

    # ========================================================
    # SERVER INFO
    # ========================================================

    @app_commands.command(
        name="serverinfo",
        description="View information about the server."
    )
    async def serverinfo(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        embed = self.embed(
            "Server Information",
            f"### {guild.name}"
        )

        embed.add_field(
            name="👥 Members",
            value=f"`{guild.member_count}`",
            inline=True
        )

        embed.add_field(
            name="💬 Channels",
            value=f"`{len(guild.channels)}`",
            inline=True
        )

        embed.add_field(
            name="🎭 Roles",
            value=f"`{len(guild.roles)}`",
            inline=True
        )

        embed.add_field(
            name="🆔 Server ID",
            value=f"`{guild.id}`",
            inline=False
        )

        if guild.icon:
            embed.set_thumbnail(
                url=guild.icon.url
            )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(Utility(bot))