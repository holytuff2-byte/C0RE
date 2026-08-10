import discord
from discord.ext import commands


# ============================================================
# C0RE TICKET TYPES
# ============================================================

TICKET_TYPES = {
    "support": {
        "label": "Support",
        "emoji": "🎫",
        "description": "Get help from the C0RE staff team."
    },
    "recruitment": {
        "label": "Recruitment",
        "emoji": "⚔️",
        "description": "Apply to join C0RE."
    },
    "partnership": {
        "label": "Partnership",
        "emoji": "🤝",
        "description": "Request a partnership with C0RE."
    },
    "report": {
        "label": "Report",
        "emoji": "🚨",
        "description": "Report a member or server issue."
    },
    "staff": {
        "label": "Staff Application",
        "emoji": "👮",
        "description": "Apply for the C0RE staff team."
    }
}


# ============================================================
# CLOSE BUTTON
# ============================================================

class CloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="core_ticket_close"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = interaction.channel

        if not isinstance(channel, discord.TextChannel):
            return

        await interaction.response.send_message(
            embed=discord.Embed(
                title="⬢ C0RE | Ticket",
                description="🔒 This ticket will be closed in 5 seconds.",
                color=0xE74C3C
            )
        )

        await discord.utils.sleep_until(
            discord.utils.utcnow()
        )

        await channel.delete(
            reason=f"Ticket closed by {interaction.user}"
        )


# ============================================================
# TICKET SELECT MENU
# ============================================================

class TicketSelect(discord.ui.Select):

    def __init__(self):

        options = []

        for ticket_id, data in TICKET_TYPES.items():

            options.append(
                discord.SelectOption(
                    label=data["label"],
                    description=data["description"],
                    emoji=data["emoji"],
                    value=ticket_id
                )
            )

        super().__init__(
            placeholder="Select a ticket category...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="core_ticket_select"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        ticket_type = self.values[0]

        data = TICKET_TYPES[ticket_type]

        guild = interaction.guild

        # ----------------------------------------------------
        # Check for existing ticket
        # ----------------------------------------------------

        existing = discord.utils.get(
            guild.text_channels,
            name=f"{ticket_type}-{interaction.user.id}"
        )

        if existing:

            return await interaction.response.send_message(
                f"❌ You already have a ticket: {existing.mention}",
                ephemeral=True
            )

        # ----------------------------------------------------
        # Find / create category
        # ----------------------------------------------------

        category_name = "C0RE TICKETS"

        category = discord.utils.get(
            guild.categories,
            name=category_name
        )

        if category is None:

            category = await guild.create_category(
                category_name,
                reason="C0RE Ticket System"
            )

        # ----------------------------------------------------
        # Permissions
        # ----------------------------------------------------

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True
                ),

            guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True
                )
        }

        # ----------------------------------------------------
        # Create channel
        # ----------------------------------------------------

        channel = await guild.create_text_channel(
            name=f"{ticket_type}-{interaction.user.id}",
            category=category,
            overwrites=overwrites,
            reason=f"C0RE {data['label']} ticket"
        )

        # ----------------------------------------------------
        # Ticket embed
        # ----------------------------------------------------

        embed = discord.Embed(
            title=f"⬢ C0RE | {data['emoji']} {data['label']}",
            description=(
                f"Welcome {interaction.user.mention}!\n\n"
                f"{data['description']}\n\n"
                "Please provide all relevant information. "
                "A member of the C0RE team will assist you."
            ),
            color=0x111111
        )

        embed.set_footer(
            text="C0RE Ticket System"
        )

        await channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"✅ Your ticket has been created: {channel.mention}",
            ephemeral=True
        )


# ============================================================
# TICKET PANEL VIEW
# ============================================================

class TicketPanelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(TicketSelect())


# ============================================================
# TICKET COG
# ============================================================

class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        # Register persistent views once.
        if not getattr(self.bot, "_core_ticket_views", False):

            self.bot.add_view(
                TicketPanelView()
            )

            self.bot.add_view(
                CloseTicketView()
            )

            self.bot._core_ticket_views = True

    @discord.app_commands.command(
        name="ticketpanel",
        description="Create the C0RE ticket panel."
    )
    @discord.app_commands.checks.has_permissions(
        manage_guild=True
    )
    async def ticketpanel(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="⬢ C0RE | Support Center",
            description=(
                "Need help from the C0RE team?\n\n"
                "Select a category below to open a private ticket.\n\n"
                "🎫 **Support**\n"
                "⚔️ **Recruitment**\n"
                "🤝 **Partnership**\n"
                "🚨 **Report**\n"
                "👮 **Staff Application**"
            ),
            color=0x111111
        )

        embed.set_footer(
            text="C0RE • Ticket System"
        )

        await interaction.channel.send(
            embed=embed,
            view=TicketPanelView()
        )

        await interaction.response.send_message(
            "✅ Ticket panel created.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))