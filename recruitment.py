import discord
from discord import app_commands
from discord.ext import commands

from database import (
    create_application,
    get_pending_applications,
    update_application_status
)


class ApplicationModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="C0RE Recruitment Application"
        )

        self.ign = discord.ui.TextInput(
            label="In-game name",
            placeholder="Your IGN / username",
            max_length=100,
            required=True
        )

        self.age = discord.ui.TextInput(
            label="Age",
            placeholder="Your age",
            max_length=3,
            required=True
        )

        self.experience = discord.ui.TextInput(
            label="Experience",
            placeholder="Tell us about your gaming/clan experience.",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )

        self.availability = discord.ui.TextInput(
            label="Availability",
            placeholder="When are you normally available?",
            style=discord.TextStyle.paragraph,
            max_length=500,
            required=True
        )

        self.add_item(self.ign)
        self.add_item(self.age)
        self.add_item(self.experience)
        self.add_item(self.availability)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        application_id = await create_application(
            interaction.guild.id,
            interaction.user.id,
            str(interaction.user),
            self.ign.value,
            self.age.value,
            self.experience.value,
            self.availability.value
        )

        embed = discord.Embed(
            title="⬢ C0RE | Application Submitted",
            description=(
                f"Your recruitment application has been submitted.\n\n"
                f"**Application:** `#{application_id}`\n"
                f"**Applicant:** {interaction.user.mention}\n\n"
                "The C0RE recruitment team will review it."
            ),
            color=0x111111
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


class ApplicationButtonView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Apply to C0RE",
        emoji="⚔️",
        style=discord.ButtonStyle.primary,
        custom_id="core_apply"
    )
    async def apply(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            ApplicationModal()
        )


class ApplicationReviewView(discord.ui.View):

    def __init__(self, application_id):
        super().__init__(timeout=None)

        self.application_id = application_id

    @discord.ui.button(
        label="Accept",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                "❌ You don't have permission to review applications.",
                ephemeral=True
            )

        await update_application_status(
            self.application_id,
            "accepted"
        )

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=f"✅ Application `#{self.application_id}` accepted by {interaction.user.mention}.",
            view=self
        )

    @discord.ui.button(
        label="Deny",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def deny(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                "❌ You don't have permission to review applications.",
                ephemeral=True
            )

        await update_application_status(
            self.application_id,
            "denied"
        )

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=f"❌ Application `#{self.application_id}` denied by {interaction.user.mention}.",
            view=self
        )


class Recruitment(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="apply",
        description="Apply to join C0RE."
    )
    async def apply(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_modal(
            ApplicationModal()
        )

    @app_commands.command(
        name="recruitmentpanel",
        description="Create the C0RE recruitment panel."
    )
    @app_commands.checks.has_permissions(
        manage_guild=True
    )
    async def recruitmentpanel(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="⬢ C0RE | Recruitment",
            description=(
                "Think you've got what it takes to join C0RE?\n\n"
                "Click **Apply to C0RE** below to submit your "
                "recruitment application.\n\n"
                "⚔️ Competitive players\n"
                "🏆 Team players\n"
                "🔥 Active members\n"
                "💪 Dedicated applicants"
            ),
            color=0x111111
        )

        embed.set_footer(
            text="C0RE • Recruitment"
        )

        await interaction.channel.send(
            embed=embed,
            view=ApplicationButtonView()
        )

        await interaction.response.send_message(
            "✅ Recruitment panel created.",
            ephemeral=True
        )

    @app_commands.command(
        name="applications",
        description="View pending C0RE recruitment applications."
    )
    @app_commands.checks.has_permissions(
        manage_guild=True
    )
    async def applications(
        self,
        interaction: discord.Interaction
    ):

        applications = await get_pending_applications(
            interaction.guild.id
        )

        if not applications:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="⬢ C0RE | Applications",
                    description="There are currently no pending applications.",
                    color=0x111111
                ),
                ephemeral=True
            )

        await interaction.response.send_message(
            embed=discord.Embed(
                title="⬢ C0RE | Applications",
                description=(
                    f"There are **{len(applications)}** pending "
                    "applications.\n\n"
                    "Applications will be sent below."
                ),
                color=0x111111
            ),
            ephemeral=True
        )

        for application in applications[:10]:

            (
                application_id,
                user_id,
                username,
                ign,
                age,
                experience,
                availability,
                created_at
            ) = application

            embed = discord.Embed(
                title=f"⚔️ C0RE Application #{application_id}",
                color=0x111111
            )

            embed.add_field(
                name="Applicant",
                value=f"<@{user_id}> (`{username}`)",
                inline=False
            )

            embed.add_field(
                name="IGN",
                value=ign,
                inline=True
            )

            embed.add_field(
                name="Age",
                value=age,
                inline=True
            )

            embed.add_field(
                name="Experience",
                value=experience[:1024],
                inline=False
            )

            embed.add_field(
                name="Availability",
                value=availability[:1024],
                inline=False
            )

            embed.set_footer(
                text=f"Submitted: {created_at}"
            )

            await interaction.channel.send(
                embed=embed,
                view=ApplicationReviewView(application_id)
            )


async def setup(bot):
    await bot.add_cog(Recruitment(bot))