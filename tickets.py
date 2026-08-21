import asyncio

import discord
from discord.ext import commands


class TicketOpenView(discord.ui.View):
    """Vue persistante avec le bouton 'Ouvrir un ticket'."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ouvrir un ticket",
        style=discord.ButtonStyle.green,
        emoji="🎫",
        custom_id="nexobot:open_ticket",
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = interaction.client
        config = bot.config
        guild = interaction.guild
        category_id = config.get("ticket_category_id")
        support_role_id = config.get("ticket_support_role_id")

        # Empêche les doublons : un seul ticket ouvert par membre
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing:
            return await interaction.response.send_message(
                f"Tu as déjà un ticket ouvert : {existing.mention}", ephemeral=True
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        if support_role_id:
            role = guild.get_role(int(support_role_id))
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        category = guild.get_channel(int(category_id)) if category_id else None

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket de {interaction.user.id}",
        )

        embed = discord.Embed(
            title="🎫 Nouveau ticket",
            description=f"Bienvenue {interaction.user.mention} ! Explique ta demande, un membre du staff va te répondre.",
            color=discord.Color.blurple(),
        )
        await channel.send(embed=embed, view=TicketCloseView())
        await interaction.response.send_message(f"Ton ticket a été créé : {channel.mention}", ephemeral=True)


class TicketCloseView(discord.ui.View):
    """Vue persistante avec le bouton 'Fermer le ticket'."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Fermer le ticket",
        style=discord.ButtonStyle.red,
        emoji="🔒",
        custom_id="nexobot:close_ticket",
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Fermeture du ticket dans 5 secondes...")
        await interaction.channel.edit(name=f"closed-{interaction.channel.name}")
        for overwrite_target in list(interaction.channel.overwrites.keys()):
            if isinstance(overwrite_target, discord.Member):
                await interaction.channel.set_permissions(overwrite_target, view_channel=False)
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Ticket fermé par {interaction.user}")


class Tickets(commands.Cog):
    """Système de tickets par boutons."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Ré-enregistre les vues au redémarrage pour que les boutons restent actifs
        bot.add_view(TicketOpenView())
        bot.add_view(TicketCloseView())

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setupticket(self, ctx: commands.Context):
        """Poste le message avec le bouton d'ouverture de ticket dans le salon actuel."""
        embed = discord.Embed(
            title="📩 Support",
            description="Clique sur le bouton ci-dessous pour ouvrir un ticket et contacter le staff.",
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed, view=TicketOpenView())
        await ctx.message.delete()


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
