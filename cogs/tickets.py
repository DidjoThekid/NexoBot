import asyncio
import io

import discord
from discord import app_commands
from discord.ext import commands

import database


class TicketOpenView(discord.ui.View):
    """Vue persistante : le bouton que les membres cliquent pour DEMANDER un ticket."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ouvrir un ticket",
        style=discord.ButtonStyle.green,
        emoji="🎫",
        custom_id="nexobot:open_ticket",
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing:
            return await interaction.response.send_message(
                f"Tu as déjà un ticket ouvert : {existing.mention}", ephemeral=True
            )

        settings = await database.get_settings(guild.id)
        review_channel_id = settings.get("ticket_review_channel_id") or settings.get("log_channel_id")
        review_channel = guild.get_channel(int(review_channel_id)) if review_channel_id else interaction.channel

        support_role_id = settings.get("ticket_support_role_id")
        role_mention = ""
        if support_role_id:
            role = guild.get_role(int(support_role_id))
            if role:
                role_mention = role.mention

        embed = discord.Embed(
            title="🎫 Nouvelle demande de ticket",
            description="Un membre souhaite ouvrir un ticket. Accepte ou refuse ci-dessous.",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Demandeur", value=f"{interaction.user.mention} ({interaction.user})", inline=False)
        embed.add_field(name="ID (technique)", value=str(interaction.user.id), inline=False)

        await review_channel.send(content=role_mention or None, embed=embed, view=TicketRequestView())
        await interaction.response.send_message(
            "✅ Ta demande a été envoyée au staff. Tu seras notifié dès qu'elle sera traitée.", ephemeral=True
        )


class TicketRequestView(discord.ui.View):
    """Vue persistante avec les boutons 'Accepter' / 'Refuser' pour le staff."""

    def __init__(self):
        super().__init__(timeout=None)

    def _is_staff(self, interaction: discord.Interaction, support_role_id) -> bool:
        if interaction.user.guild_permissions.manage_guild:
            return True
        if support_role_id:
            role = interaction.guild.get_role(int(support_role_id))
            if role and role in interaction.user.roles:
                return True
        return False

    def _get_requester_id(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        for field in embed.fields:
            if field.name == "ID (technique)":
                return int(field.value)
        return None

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green, emoji="✅", custom_id="nexobot:accept_ticket")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = await database.get_settings(interaction.guild.id)
        if not self._is_staff(interaction, settings.get("ticket_support_role_id")):
            return await interaction.response.send_message("🚫 Tu n'as pas la permission de traiter cette demande.", ephemeral=True)

        requester_id = self._get_requester_id(interaction)
        requester = interaction.guild.get_member(requester_id) if requester_id else None
        if not requester:
            return await interaction.response.send_message("⚠️ Ce membre n'est plus sur le serveur.", ephemeral=True)

        category_id = settings.get("ticket_category_id")
        support_role_id = settings.get("ticket_support_role_id")

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            requester: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        if support_role_id:
            role = interaction.guild.get_role(int(support_role_id))
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        category = interaction.guild.get_channel(int(category_id)) if category_id else None

        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{requester.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket de {requester.id}",
        )

        welcome_embed = discord.Embed(
            title="🎫 Ticket ouvert",
            description=f"Bienvenue {requester.mention} ! Explique ta demande, un membre du staff va te répondre.",
            color=discord.Color.blurple(),
        )
        await channel.send(embed=welcome_embed, view=TicketCloseView())

        accepted_embed = interaction.message.embeds[0].copy()
        accepted_embed.title = "✅ Demande de ticket acceptée"
        accepted_embed.color = discord.Color.green()
        accepted_embed.add_field(name="Traité par", value=interaction.user.mention, inline=False)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=accepted_embed, view=self)

        try:
            await requester.send(f"✅ Ton ticket sur **{interaction.guild.name}** a été accepté : {channel.mention}")
        except discord.Forbidden:
            pass

    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.red, emoji="❌", custom_id="nexobot:refuse_ticket")
    async def refuse(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = await database.get_settings(interaction.guild.id)
        if not self._is_staff(interaction, settings.get("ticket_support_role_id")):
            return await interaction.response.send_message("🚫 Tu n'as pas la permission de traiter cette demande.", ephemeral=True)

        requester_id = self._get_requester_id(interaction)
        requester = interaction.guild.get_member(requester_id) if requester_id else None

        refused_embed = interaction.message.embeds[0].copy()
        refused_embed.title = "❌ Demande de ticket refusée"
        refused_embed.color = discord.Color.red()
        refused_embed.add_field(name="Traité par", value=interaction.user.mention, inline=False)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=refused_embed, view=self)

        if requester:
            try:
                await requester.send(f"❌ Ta demande de ticket sur **{interaction.guild.name}** a été refusée.")
            except discord.Forbidden:
                pass


class TicketCloseView(discord.ui.View):
    """Vue persistante avec le bouton 'Fermer le ticket'. Exporte la conversation en .txt avant suppression."""

    def __init__(self):
        super().__init__(timeout=None)

    async def _build_transcript(self, channel: discord.TextChannel) -> discord.File:
        lines = [f"Transcript du ticket : {channel.name}", "=" * 50, ""]
        async for message in channel.history(limit=None, oldest_first=True):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            content = message.content or "*(aucun texte)*"
            lines.append(f"[{timestamp}] {message.author} : {content}")
            for attachment in message.attachments:
                lines.append(f"    📎 Pièce jointe : {attachment.url}")
        transcript_text = "\n".join(lines)
        buffer = io.BytesIO(transcript_text.encode("utf-8"))
        return discord.File(buffer, filename=f"transcript-{channel.name}.txt")

    @discord.ui.button(
        label="Fermer le ticket",
        style=discord.ButtonStyle.red,
        emoji="🔒",
        custom_id="nexobot:close_ticket",
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Génération du transcript et fermeture dans 5 secondes...")

        channel = interaction.channel
        guild = interaction.guild

        settings = await database.get_settings(guild.id)
        log_channel_id = settings.get("log_channel_id")
        log_channel = guild.get_channel(int(log_channel_id)) if log_channel_id else None

        embed = discord.Embed(
            title="🔒 Ticket fermé",
            description=f"Salon **{channel.name}** fermé par {interaction.user.mention}",
            color=discord.Color.dark_grey(),
        )

        if log_channel:
            await log_channel.send(embed=embed, file=await self._build_transcript(channel))
        else:
            await channel.send(embed=embed, file=await self._build_transcript(channel))

        requester_id = None
        if channel.topic and channel.topic.startswith("Ticket de "):
            try:
                requester_id = int(channel.topic.replace("Ticket de ", "").strip())
            except ValueError:
                requester_id = None

        if requester_id:
            requester = guild.get_member(requester_id)
            if requester:
                try:
                    await requester.send(
                        f"Voici le transcript de ton ticket sur **{guild.name}** :",
                        file=await self._build_transcript(channel),
                    )
                except discord.Forbidden:
                    pass

        await channel.edit(name=f"closed-{channel.name}")
        for overwrite_target in list(channel.overwrites.keys()):
            if isinstance(overwrite_target, discord.Member):
                await channel.set_permissions(overwrite_target, view_channel=False)
        await asyncio.sleep(5)
        await channel.delete(reason=f"Ticket fermé par {interaction.user}")


class Tickets(commands.Cog):
    """Système de tickets par boutons avec validation staff et transcript."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(TicketOpenView())
        bot.add_view(TicketRequestView())
        bot.add_view(TicketCloseView())

    @app_commands.command(name="setupticket", description="Poste le message d'ouverture de ticket dans ce salon.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setupticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📩 Support",
            description="Clique sur le bouton ci-dessous pour demander l'ouverture d'un ticket.",
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed, view=TicketOpenView())


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
