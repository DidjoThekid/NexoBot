import discord
from discord.ext import commands

import database


class Settings(commands.Cog):
    """Commandes de configuration du bot, par serveur."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx: commands.Context, new_prefix: str):
        if len(new_prefix) > 5:
            return await ctx.send("Le préfixe doit faire 5 caractères maximum.")
        await database.update_setting(ctx.guild.id, "prefix", new_prefix)
        await ctx.send(f"✅ Préfixe mis à jour : `{new_prefix}`")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setlogchannel(self, ctx: commands.Context, channel: discord.TextChannel):
        await database.update_setting(ctx.guild.id, "log_channel_id", channel.id)
        await ctx.send(f"✅ Salon de logs défini sur {channel.mention}.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcomechannel(self, ctx: commands.Context, channel: discord.TextChannel):
        await database.update_setting(ctx.guild.id, "welcome_channel_id", channel.id)
        await ctx.send(f"✅ Salon de bienvenue défini sur {channel.mention}.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcomemessage(self, ctx: commands.Context, *, message: str):
        """Variables disponibles : {mention} {member} {server} {count}"""
        await database.update_setting(ctx.guild.id, "welcome_message", message)
        await ctx.send("✅ Message de bienvenue mis à jour.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setticketcategory(self, ctx: commands.Context, category: discord.CategoryChannel):
        await database.update_setting(ctx.guild.id, "ticket_category_id", category.id)
        await ctx.send(f"✅ Catégorie de tickets définie sur **{category.name}**.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setsupportrole(self, ctx: commands.Context, role: discord.Role):
        await database.update_setting(ctx.guild.id, "ticket_support_role_id", role.id)
        await ctx.send(f"✅ Rôle support défini sur {role.mention}.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx: commands.Context):
        """Affiche la configuration actuelle du serveur."""
        s = await database.get_settings(ctx.guild.id)

        def fmt_channel(cid):
            return ctx.guild.get_channel(int(cid)).mention if cid and ctx.guild.get_channel(int(cid)) else "Non défini"

        def fmt_role(rid):
            role = ctx.guild.get_role(int(rid)) if rid else None
            return role.mention if role else "Non défini"

        embed = discord.Embed(title=f"⚙️ Configuration de {ctx.guild.name}", color=discord.Color.blurple())
        embed.add_field(name="Préfixe", value=f"`{s['prefix']}`", inline=True)
        embed.add_field(name="Automod", value="Activé ✅" if s["automod_enabled"] else "Désactivé ❌", inline=True)
        embed.add_field(name="Salon de logs", value=fmt_channel(s["log_channel_id"]), inline=True)
        embed.add_field(name="Salon de bienvenue", value=fmt_channel(s["welcome_channel_id"]), inline=True)
        embed.add_field(name="Catégorie tickets", value=fmt_channel(s["ticket_category_id"]), inline=True)
        embed.add_field(name="Rôle support", value=fmt_role(s["ticket_support_role_id"]), inline=True)
        embed.add_field(name="Message de bienvenue", value=s["welcome_message"], inline=False)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))
