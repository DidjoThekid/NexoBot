import datetime

import discord
from discord.ext import commands

import database


class Logs(commands.Cog):
    """Journalise les événements importants du serveur dans un salon dédié."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_log_channel(self, guild: discord.Guild):
        settings = await database.get_settings(guild.id)
        log_channel_id = settings.get("log_channel_id")
        if not log_channel_id:
            return None
        return guild.get_channel(int(log_channel_id))

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        channel = await self._get_log_channel(message.guild)
        if not channel:
            return

        embed = discord.Embed(
            title="🗑️ Message supprimé",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.add_field(name="Auteur", value=str(message.author), inline=True)
        embed.add_field(name="Salon", value=message.channel.mention, inline=True)
        embed.add_field(name="Contenu", value=message.content or "*(aucun texte, pièce jointe ?)*", inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        channel = await self._get_log_channel(before.guild)
        if not channel:
            return

        embed = discord.Embed(
            title="✏️ Message modifié",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.add_field(name="Auteur", value=str(before.author), inline=True)
        embed.add_field(name="Salon", value=before.channel.mention, inline=True)
        embed.add_field(name="Avant", value=before.content or "*(vide)*", inline=False)
        embed.add_field(name="Après", value=after.content or "*(vide)*", inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = await self._get_log_channel(member.guild)
        if not channel:
            return
        embed = discord.Embed(
            title="📥 Arrivée d'un membre",
            description=f"{member.mention} ({member})",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = await self._get_log_channel(member.guild)
        if not channel:
            return
        embed = discord.Embed(
            title="📤 Départ d'un membre",
            description=f"{member.mention} ({member})",
            color=discord.Color.dark_grey(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        channel = await self._get_log_channel(guild)
        if not channel:
            return
        embed = discord.Embed(
            title="🔨 Utilisateur banni",
            description=f"{user.mention} ({user})",
            color=discord.Color.dark_red(),
            timestamp=datetime.datetime.utcnow(),
        )
        await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Logs(bot))
