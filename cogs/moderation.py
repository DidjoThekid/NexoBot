import datetime

import discord
from discord import app_commands
from discord.ext import commands

import database


class Moderation(commands.Cog):
    """Commandes de modération : kick, ban, mute, clear, warn."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _log(self, guild: discord.Guild, embed: discord.Embed):
        settings = await database.get_settings(guild.id)
        log_channel_id = settings.get("log_channel_id")
        if not log_channel_id:
            return
        channel = guild.get_channel(int(log_channel_id))
        if channel:
            await channel.send(embed=embed)

    # ------------------------------------------------------------------
    # Kick
    # ------------------------------------------------------------------
    @app_commands.command(name="kick", description="Expulse un membre du serveur.")
    @app_commands.describe(member="Le membre à expulser", reason="Raison de l'expulsion")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
        if member == interaction.user:
            return await interaction.response.send_message("Tu ne peux pas t'exclure toi-même.", ephemeral=True)
        if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            return await interaction.response.send_message(
                "Tu ne peux pas expulser quelqu'un avec un rôle égal ou supérieur au tien.", ephemeral=True
            )

        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Membre expulsé", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Modérateur", value=str(interaction.user), inline=False)
        embed.add_field(name="Raison", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, embed)

    # ------------------------------------------------------------------
    # Ban / Unban
    # ------------------------------------------------------------------
    @app_commands.command(name="ban", description="Bannit un membre du serveur.")
    @app_commands.describe(member="Le membre à bannir", reason="Raison du bannissement")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
        if member == interaction.user:
            return await interaction.response.send_message("Tu ne peux pas te bannir toi-même.", ephemeral=True)
        if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            return await interaction.response.send_message(
                "Tu ne peux pas bannir quelqu'un avec un rôle égal ou supérieur au tien.", ephemeral=True
            )

        await member.ban(reason=reason, delete_message_days=0)
        embed = discord.Embed(
            title="🔨 Membre banni", color=discord.Color.red(), timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Modérateur", value=str(interaction.user), inline=False)
        embed.add_field(name="Raison", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, embed)

    @app_commands.command(name="unban", description="Débannit un utilisateur via son ID.")
    @app_commands.describe(user_id="L'ID Discord de l'utilisateur à débannir")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ {user} a été débanni.")
        except (discord.NotFound, ValueError):
            await interaction.response.send_message("Cet utilisateur n'est pas banni ou l'ID est invalide.", ephemeral=True)

    # ------------------------------------------------------------------
    # Timeout (mute temporaire natif Discord)
    # ------------------------------------------------------------------
    @app_commands.command(name="mute", description="Met un membre en sourdine (timeout) pour une durée donnée.")
    @app_commands.describe(member="Le membre à mute", minutes="Durée en minutes (max 40320 = 28 jours)", reason="Raison")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Aucune raison fournie"):
        if minutes <= 0 or minutes > 40320:
            return await interaction.response.send_message(
                "La durée doit être comprise entre 1 et 40320 minutes (28 jours).", ephemeral=True
            )

        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(
            title="🔇 Membre mis en sourdine", color=discord.Color.gold(), timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Durée", value=f"{minutes} minute(s)", inline=False)
        embed.add_field(name="Modérateur", value=str(interaction.user), inline=False)
        embed.add_field(name="Raison", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, embed)

    @app_commands.command(name="unmute", description="Retire le timeout d'un membre.")
    @app_commands.describe(member="Le membre à réactiver")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(f"🔊 {member.mention} n'est plus en sourdine.")

    # ------------------------------------------------------------------
    # Clear / purge
    # ------------------------------------------------------------------
    @app_commands.command(name="clear", description="Supprime un nombre de messages dans le salon actuel.")
    @app_commands.describe(amount="Nombre de messages à supprimer (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount <= 0 or amount > 100:
            return await interaction.response.send_message("Merci de choisir un nombre entre 1 et 100.", ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 {len(deleted)} message(s) supprimé(s).", ephemeral=True)

    # ------------------------------------------------------------------
    # Warn system (stocké en base, par serveur)
    # ------------------------------------------------------------------
    @app_commands.command(name="warn", description="Donne un avertissement à un membre.")
    @app_commands.describe(member="Le membre à avertir", reason="Raison de l'avertissement")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
        count = await database.add_warning(
            interaction.guild.id, member.id, str(interaction.user), reason, datetime.datetime.utcnow().isoformat()
        )

        embed = discord.Embed(title="⚠️ Avertissement", color=discord.Color.yellow(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Total d'avertissements", value=str(count), inline=False)
        embed.add_field(name="Raison", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, embed)

        try:
            await member.send(f"Tu as reçu un avertissement sur **{interaction.guild.name}** : {reason}")
        except discord.Forbidden:
            pass

    @app_commands.command(name="warnings", description="Affiche les avertissements d'un membre.")
    @app_commands.describe(member="Le membre à consulter (toi-même par défaut)")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        entries = await database.get_warnings(interaction.guild.id, member.id)

        if not entries:
            return await interaction.response.send_message(f"{member.mention} n'a aucun avertissement.", ephemeral=True)

        embed = discord.Embed(title=f"Avertissements de {member}", color=discord.Color.yellow())
        for i, entry in enumerate(entries, start=1):
            embed.add_field(
                name=f"#{i} — {entry['created_at'][:10]}",
                value=f"Par {entry['moderator']} : {entry['reason']}",
                inline=False,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clearwarns", description="Réinitialise les avertissements d'un membre.")
    @app_commands.describe(member="Le membre concerné")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def clearwarns(self, interaction: discord.Interaction, member: discord.Member):
        await database.clear_warnings(interaction.guild.id, member.id)
        await interaction.response.send_message(f"✅ Avertissements de {member.mention} réinitialisés.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
