import discord
from discord.ext import commands


class Utility(commands.Cog):
    """Commandes utiles diverses."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong ! Latence : {latency_ms}ms")

    @commands.command()
    async def userinfo(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Informations sur {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Surnom", value=member.nick or "Aucun", inline=True)
        embed.add_field(name="Bot ?", value="Oui" if member.bot else "Non", inline=True)
        embed.add_field(
            name="Compte créé le",
            value=discord.utils.format_dt(member.created_at, style="D"),
            inline=True,
        )
        embed.add_field(
            name="A rejoint le",
            value=discord.utils.format_dt(member.joined_at, style="D") if member.joined_at else "Inconnu",
            inline=True,
        )
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        embed.add_field(name=f"Rôles ({len(roles)})", value=" ".join(roles) if roles else "Aucun", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Propriétaire", value=str(guild.owner), inline=True)
        embed.add_field(name="Membres", value=guild.member_count, inline=True)
        embed.add_field(name="Salons textuels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Salons vocaux", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="Rôles", value=len(guild.roles), inline=True)
        embed.add_field(
            name="Créé le",
            value=discord.utils.format_dt(guild.created_at, style="D"),
            inline=True,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Avatar de {member}", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
