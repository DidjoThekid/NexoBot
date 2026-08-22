import discord
from discord import app_commands
from discord.ext import commands


class Utility(commands.Cog):
    """Commandes utiles diverses."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Affiche la latence du bot.")
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong ! Latence : {latency_ms}ms")

    @app_commands.command(name="userinfo", description="Affiche les informations d'un membre.")
    @app_commands.describe(member="Le membre à consulter (toi-même par défaut)")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"Informations sur {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Surnom", value=member.nick or "Aucun", inline=True)
        embed.add_field(name="Bot ?", value="Oui" if member.bot else "Non", inline=True)
        embed.add_field(
            name="Compte créé le", value=discord.utils.format_dt(member.created_at, style="D"), inline=True
        )
        embed.add_field(
            name="A rejoint le",
            value=discord.utils.format_dt(member.joined_at, style="D") if member.joined_at else "Inconnu",
            inline=True,
        )
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        embed.add_field(name=f"Rôles ({len(roles)})", value=" ".join(roles) if roles else "Aucun", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Affiche les informations du serveur.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Propriétaire", value=str(guild.owner), inline=True)
        embed.add_field(name="Membres", value=guild.member_count, inline=True)
        embed.add_field(name="Salons textuels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Salons vocaux", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="Rôles", value=len(guild.roles), inline=True)
        embed.add_field(name="Créé le", value=discord.utils.format_dt(guild.created_at, style="D"), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Affiche l'avatar d'un membre en grand.")
    @app_commands.describe(member="Le membre à consulter (toi-même par défaut)")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"Avatar de {member}", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
