import datetime
import json
import os

import discord
from discord.ext import commands

WARN_FILE = "warnings.json"


def _load_warnings() -> dict:
    if not os.path.exists(WARN_FILE):
        return {}
    with open(WARN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_warnings(data: dict) -> None:
    with open(WARN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class Moderation(commands.Cog):
    """Commandes de modération : kick, ban, mute, clear, warn."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _log(self, guild: discord.Guild, embed: discord.Embed):
        """Envoie un embed dans le salon de logs configuré, si présent."""
        log_channel_id = self.bot.config.get("log_channel_id")
        if not log_channel_id:
            return
        channel = guild.get_channel(int(log_channel_id))
        if channel:
            await channel.send(embed=embed)

    # ------------------------------------------------------------------
    # Kick
    # ------------------------------------------------------------------
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison fournie"):
        if member == ctx.author:
            return await ctx.send("Tu ne peux pas t'exclure toi-même.")
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("Tu ne peux pas expulser quelqu'un avec un rôle égal ou supérieur au tien.")

        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Membre expulsé",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Modérateur", value=str(ctx.author), inline=False)
        embed.add_field(name="Raison", value=reason, inline=False)
        await ctx.send(embed=embed)
        await self._log(ctx.guild, embed)

    # ------------------------------------------------------------------
    # Ban / Unban
    # ------------------------------------------------------------------
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison fournie"):
        if member == ctx.author:
            return await ctx.send("Tu ne peux pas te bannir toi-même.")
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("Tu ne peux pas bannir quelqu'un avec un rôle égal ou supérieur au tien.")

        await member.ban(reason=reason, delete_message_days=0)
        embed = discord.Embed(
            title="🔨 Membre banni",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Modérateur", value=str(ctx.author), inline=False)
        embed.add_field(name="Raison", value=reason, inline=False)
        await ctx.send(embed=embed)
        await self._log(ctx.guild, embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user} a été débanni.")
        except discord.NotFound:
            await ctx.send("Cet utilisateur n'est pas banni ou n'existe pas.")

    # ------------------------------------------------------------------
    # Timeout (mute temporaire natif Discord)
    # ------------------------------------------------------------------
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, minutes: int, *, reason: str = "Aucune raison fournie"):
        if minutes <= 0 or minutes > 40320:  # max 28 jours
            return await ctx.send("La durée doit être comprise entre 1 et 40320 minutes (28 jours).")

        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        embed = discord.Embed(
            title="🔇 Membre mis en sourdine",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Durée", value=f"{minutes} minute(s)", inline=False)
        embed.add_field(name="Modérateur", value=str(ctx.author), inline=False)
        embed.add_field(name="Raison", value=reason, inline=False)
        await ctx.send(embed=embed)
        await self._log(ctx.guild, embed)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 {member.mention} n'est plus en sourdine.")

    # ------------------------------------------------------------------
    # Clear / purge
    # ------------------------------------------------------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int):
        if amount <= 0 or amount > 100:
            return await ctx.send("Merci de choisir un nombre entre 1 et 100.")
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 pour inclure la commande elle-même
        msg = await ctx.send(f"🧹 {len(deleted) - 1} message(s) supprimé(s).")
        await msg.delete(delay=3)

    # ------------------------------------------------------------------
    # Warn system (stocké dans warnings.json)
    # ------------------------------------------------------------------
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Aucune raison fournie"):
        data = _load_warnings()
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        data.setdefault(guild_id, {}).setdefault(user_id, [])
        data[guild_id][user_id].append({
            "reason": reason,
            "moderator": str(ctx.author),
            "date": datetime.datetime.utcnow().isoformat(),
        })
        _save_warnings(data)

        count = len(data[guild_id][user_id])
        embed = discord.Embed(
            title="⚠️ Avertissement",
            color=discord.Color.yellow(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.add_field(name="Membre", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Total d'avertissements", value=str(count), inline=False)
        embed.add_field(name="Raison", value=reason, inline=False)
        await ctx.send(embed=embed)
        await self._log(ctx.guild, embed)

        try:
            await member.send(f"Tu as reçu un avertissement sur **{ctx.guild.name}** : {reason}")
        except discord.Forbidden:
            pass  # MP fermés, tant pis

    @commands.command()
    async def warnings(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        data = _load_warnings()
        entries = data.get(str(ctx.guild.id), {}).get(str(member.id), [])

        if not entries:
            return await ctx.send(f"{member.mention} n'a aucun avertissement.")

        embed = discord.Embed(title=f"Avertissements de {member}", color=discord.Color.yellow())
        for i, entry in enumerate(entries, start=1):
            embed.add_field(
                name=f"#{i} — {entry['date'][:10]}",
                value=f"Par {entry['moderator']} : {entry['reason']}",
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def clearwarns(self, ctx: commands.Context, member: discord.Member):
        data = _load_warnings()
        data.get(str(ctx.guild.id), {}).pop(str(member.id), None)
        _save_warnings(data)
        await ctx.send(f"✅ Avertissements de {member.mention} réinitialisés.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
