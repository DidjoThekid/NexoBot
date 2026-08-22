import discord
from discord import app_commands
from discord.ext import commands

import database


class Settings(commands.Cog):
    """Commandes de configuration du bot, par serveur."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setlogchannel", description="Définit le salon où sont envoyés les logs.")
    @app_commands.describe(channel="Le salon de destination des logs")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setlogchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await database.update_setting(interaction.guild.id, "log_channel_id", channel.id)
        await interaction.response.send_message(f"✅ Salon de logs défini sur {channel.mention}.")

    @app_commands.command(name="setwelcomechannel", description="Définit le salon de bienvenue.")
    @app_commands.describe(channel="Le salon où seront postés les messages d'accueil")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setwelcomechannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await database.update_setting(interaction.guild.id, "welcome_channel_id", channel.id)
        await interaction.response.send_message(f"✅ Salon de bienvenue défini sur {channel.mention}.")

    @app_commands.command(name="setwelcomemessage", description="Personnalise le message de bienvenue.")
    @app_commands.describe(message="Variables disponibles : {mention} {member} {server} {count}")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setwelcomemessage(self, interaction: discord.Interaction, message: str):
        await database.update_setting(interaction.guild.id, "welcome_message", message)
        await interaction.response.send_message("✅ Message de bienvenue mis à jour.")

    @app_commands.command(name="setticketcategory", description="Définit la catégorie où sont créés les tickets.")
    @app_commands.describe(category="La catégorie de destination des tickets")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setticketcategory(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        await database.update_setting(interaction.guild.id, "ticket_category_id", category.id)
        await interaction.response.send_message(f"✅ Catégorie de tickets définie sur **{category.name}**.")

    @app_commands.command(name="setsupportrole", description="Définit le rôle ajouté automatiquement aux tickets.")
    @app_commands.describe(role="Le rôle du staff support")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setsupportrole(self, interaction: discord.Interaction, role: discord.Role):
        await database.update_setting(interaction.guild.id, "ticket_support_role_id", role.id)
        await interaction.response.send_message(f"✅ Rôle support défini sur {role.mention}.")

    @app_commands.command(name="settings", description="Affiche la configuration actuelle du serveur.")
    async def settings(self, interaction: discord.Interaction):
        s = await database.get_settings(interaction.guild.id)

        def fmt_channel(cid):
            return interaction.guild.get_channel(int(cid)).mention if cid and interaction.guild.get_channel(int(cid)) else "Non défini"

        def fmt_role(rid):
            role = interaction.guild.get_role(int(rid)) if rid else None
            return role.mention if role else "Non défini"

        embed = discord.Embed(title=f"⚙️ Configuration de {interaction.guild.name}", color=discord.Color.blurple())
        embed.add_field(name="Automod", value="Activé ✅" if s["automod_enabled"] else "Désactivé ❌", inline=True)
        embed.add_field(name="Salon de logs", value=fmt_channel(s["log_channel_id"]), inline=True)
        embed.add_field(name="Salon de bienvenue", value=fmt_channel(s["welcome_channel_id"]), inline=True)
        embed.add_field(name="Catégorie tickets", value=fmt_channel(s["ticket_category_id"]), inline=True)
        embed.add_field(name="Rôle support", value=fmt_role(s["ticket_support_role_id"]), inline=True)
        embed.add_field(name="Message de bienvenue", value=s["welcome_message"], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))
