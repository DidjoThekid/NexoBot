import discord
from discord import app_commands
from discord.ext import commands

import database


class Config(commands.Cog):
    """Toutes les commandes de configuration du bot, regroupées sous /config."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    config_group = app_commands.Group(
        name="config",
        description="Configure NexoBot pour ce serveur.",
        default_permissions=discord.Permissions(manage_guild=True),
    )

    # ------------------------------------------------------------------
    # Logs / Bienvenue
    # ------------------------------------------------------------------
    @config_group.command(name="logchannel", description="Définit le salon où sont envoyés les logs.")
    @app_commands.describe(channel="Le salon de destination des logs")
    async def logchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await database.update_setting(interaction.guild.id, "log_channel_id", channel.id)
        await interaction.response.send_message(f"✅ Salon de logs défini sur {channel.mention}.", ephemeral=True)

    @config_group.command(name="welcomechannel", description="Définit le salon de bienvenue.")
    @app_commands.describe(channel="Le salon où seront postés les messages d'accueil")
    async def welcomechannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await database.update_setting(interaction.guild.id, "welcome_channel_id", channel.id)
        await interaction.response.send_message(f"✅ Salon de bienvenue défini sur {channel.mention}.", ephemeral=True)

    @config_group.command(name="welcomemessage", description="Personnalise le message de bienvenue.")
    @app_commands.describe(message="Variables disponibles : {mention} {member} {server} {count}")
    async def welcomemessage(self, interaction: discord.Interaction, message: str):
        await database.update_setting(interaction.guild.id, "welcome_message", message)
        await interaction.response.send_message("✅ Message de bienvenue mis à jour.", ephemeral=True)

    # ------------------------------------------------------------------
    # Tickets
    # ------------------------------------------------------------------
    @config_group.command(name="ticketcategory", description="Définit la catégorie où sont créés les tickets.")
    @app_commands.describe(category="La catégorie de destination des tickets")
    async def ticketcategory(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        await database.update_setting(interaction.guild.id, "ticket_category_id", category.id)
        await interaction.response.send_message(f"✅ Catégorie de tickets définie sur **{category.name}**.", ephemeral=True)

    @config_group.command(name="supportrole", description="Définit le rôle staff pour les tickets.")
    @app_commands.describe(role="Le rôle du staff support")
    async def supportrole(self, interaction: discord.Interaction, role: discord.Role):
        await database.update_setting(interaction.guild.id, "ticket_support_role_id", role.id)
        await interaction.response.send_message(f"✅ Rôle support défini sur {role.mention}.", ephemeral=True)

    @config_group.command(
        name="ticketreviewchannel",
        description="Salon où le staff reçoit les demandes de ticket à accepter/refuser.",
    )
    @app_commands.describe(channel="Le salon de review des demandes de ticket")
    async def ticketreviewchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await database.update_setting(interaction.guild.id, "ticket_review_channel_id", channel.id)
        await interaction.response.send_message(
            f"✅ Les demandes de ticket seront envoyées dans {channel.mention}.", ephemeral=True
        )

    # ------------------------------------------------------------------
    # Automod
    # ------------------------------------------------------------------
    @config_group.command(name="automod", description="Active ou désactive le filtre automatique.")
    @app_commands.describe(state="on pour activer, off pour désactiver")
    @app_commands.choices(state=[
        app_commands.Choice(name="on", value="on"),
        app_commands.Choice(name="off", value="off"),
    ])
    async def automod(self, interaction: discord.Interaction, state: app_commands.Choice[str]):
        await database.update_setting(interaction.guild.id, "automod_enabled", state.value == "on")
        await interaction.response.send_message(
            f"✅ Automod {'activé' if state.value == 'on' else 'désactivé'}.", ephemeral=True
        )

    @config_group.command(name="addbannedword", description="Ajoute un mot à la liste des mots interdits.")
    @app_commands.describe(word="Le mot à interdire")
    async def addbannedword(self, interaction: discord.Interaction, word: str):
        await database.add_banned_word(interaction.guild.id, word)
        await interaction.response.send_message("✅ Mot ajouté à la liste des mots interdits.", ephemeral=True)

    @config_group.command(name="removebannedword", description="Retire un mot de la liste des mots interdits.")
    @app_commands.describe(word="Le mot à retirer")
    async def removebannedword(self, interaction: discord.Interaction, word: str):
        await database.remove_banned_word(interaction.guild.id, word)
        await interaction.response.send_message("✅ Mot retiré de la liste des mots interdits.", ephemeral=True)

    @config_group.command(name="bannedwords", description="Envoie en MP la liste des mots interdits.")
    async def bannedwords(self, interaction: discord.Interaction):
        words = await database.get_banned_words(interaction.guild.id)
        if not words:
            return await interaction.response.send_message("Aucun mot interdit configuré.", ephemeral=True)
        try:
            await interaction.user.send("Mots interdits sur ce serveur :\n" + ", ".join(f"`{w}`" for w in words))
            await interaction.response.send_message("📬 Je t'ai envoyé la liste en message privé.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Active tes MP pour que je puisse t'envoyer la liste.", ephemeral=True)

    # ------------------------------------------------------------------
    # Vue d'ensemble
    # ------------------------------------------------------------------
    @config_group.command(name="view", description="Affiche la configuration actuelle du serveur.")
    async def view(self, interaction: discord.Interaction):
        s = await database.get_settings(interaction.guild.id)

        def fmt_channel(cid):
            ch = interaction.guild.get_channel(int(cid)) if cid else None
            return ch.mention if ch else "Non défini"

        def fmt_role(rid):
            role = interaction.guild.get_role(int(rid)) if rid else None
            return role.mention if role else "Non défini"

        embed = discord.Embed(title=f"⚙️ Configuration de {interaction.guild.name}", color=discord.Color.blurple())
        embed.add_field(name="Automod", value="Activé ✅" if s["automod_enabled"] else "Désactivé ❌", inline=True)
        embed.add_field(name="Salon de logs", value=fmt_channel(s["log_channel_id"]), inline=True)
        embed.add_field(name="Salon de bienvenue", value=fmt_channel(s["welcome_channel_id"]), inline=True)
        embed.add_field(name="Catégorie tickets", value=fmt_channel(s["ticket_category_id"]), inline=True)
        embed.add_field(name="Rôle support", value=fmt_role(s["ticket_support_role_id"]), inline=True)
        embed.add_field(name="Salon review tickets", value=fmt_channel(s["ticket_review_channel_id"]), inline=True)
        embed.add_field(name="Message de bienvenue", value=s["welcome_message"], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))
