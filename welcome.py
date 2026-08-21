import discord
from discord.ext import commands


class Welcome(commands.Cog):
    """Envoie un message de bienvenue lorsqu'un membre rejoint le serveur."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel_id = self.bot.config.get("welcome_channel_id")
        if not channel_id:
            return

        channel = member.guild.get_channel(int(channel_id))
        if not channel:
            return

        template = self.bot.config.get(
            "welcome_message",
            "Bienvenue {mention} sur **{server}** ! Tu es notre {count}e membre 🎉",
        )
        text = template.format(
            mention=member.mention,
            member=member.name,
            server=member.guild.name,
            count=member.guild.member_count,
        )

        embed = discord.Embed(description=text, color=discord.Color.blurple())
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcome(self, ctx: commands.Context, channel: discord.TextChannel):
        """Définit le salon de bienvenue (persiste seulement pour la session en cours)."""
        self.bot.config["welcome_channel_id"] = channel.id
        await ctx.send(
            f"✅ Le salon de bienvenue est maintenant {channel.mention}.\n"
            f"⚠️ Pense à mettre à jour `welcome_channel_id` dans `config.json` pour que ce soit permanent."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
