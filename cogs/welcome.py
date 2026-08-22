import discord
from discord.ext import commands

import database


class Welcome(commands.Cog):
    """Envoie un message de bienvenue lorsqu'un membre rejoint le serveur."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = await database.get_settings(member.guild.id)
        channel_id = settings.get("welcome_channel_id")
        if not channel_id:
            return

        channel = member.guild.get_channel(int(channel_id))
        if not channel:
            return

        template = settings.get(
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
