import time
from collections import defaultdict, deque

import discord
from discord.ext import commands

import database

# Anti-spam : fenêtre glissante en mémoire (pas besoin de DB, c'est éphémère)
SPAM_WINDOW_SECONDS = 6
SPAM_MESSAGE_THRESHOLD = 5  # N messages en moins de SPAM_WINDOW_SECONDS = spam

_message_history: dict[int, deque] = defaultdict(deque)


class AutoMod(commands.Cog):
    """Filtre de mots interdits et détection basique de spam."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        settings = await database.get_settings(message.guild.id)
        if not settings.get("automod_enabled"):
            return

        # Le staff (permission manage_messages) n'est pas soumis à l'automod
        if isinstance(message.author, discord.Member) and message.author.guild_permissions.manage_messages:
            return

        if await self._check_banned_words(message, settings):
            return
        await self._check_spam(message, settings)

    async def _check_banned_words(self, message: discord.Message, settings: dict) -> bool:
        banned_words = await database.get_banned_words(message.guild.id)
        if not banned_words:
            return False

        content_lower = message.content.lower()
        if any(word in content_lower for word in banned_words):
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            warning = await message.channel.send(
                f"{message.author.mention} ton message a été supprimé (mot interdit).",
                delete_after=5,
            )
            await self._log_automod(message.guild, settings, message.author, "Mot interdit", message.content)
            return True
        return False

    async def _check_spam(self, message: discord.Message, settings: dict) -> None:
        now = time.time()
        history = _message_history[message.author.id]
        history.append(now)

        # On ne garde que les messages dans la fenêtre de temps
        while history and now - history[0] > SPAM_WINDOW_SECONDS:
            history.popleft()

        if len(history) >= SPAM_MESSAGE_THRESHOLD:
            history.clear()
            try:
                await message.channel.set_permissions(
                    message.author, send_messages=False, reason="Anti-spam automatique"
                )
            except discord.Forbidden:
                pass
            await message.channel.send(
                f"🚫 {message.author.mention} a été mis en sourdine sur ce salon pour spam."
            )
            await self._log_automod(
                message.guild, settings, message.author, "Spam détecté",
                f"{SPAM_MESSAGE_THRESHOLD} messages en moins de {SPAM_WINDOW_SECONDS}s"
            )

    async def _log_automod(self, guild, settings, member, reason, detail):
        log_channel_id = settings.get("log_channel_id")
        if not log_channel_id:
            return
        channel = guild.get_channel(int(log_channel_id))
        if not channel:
            return
        embed = discord.Embed(title="🛡️ Automod", color=discord.Color.dark_orange())
        embed.add_field(name="Membre", value=str(member), inline=True)
        embed.add_field(name="Motif", value=reason, inline=True)
        embed.add_field(name="Détail", value=detail[:1000], inline=False)
        await channel.send(embed=embed)

    # ------------------------------------------------------------------
    # Commandes de gestion
    # ------------------------------------------------------------------
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def automod(self, ctx: commands.Context, state: str):
        if state.lower() not in ("on", "off"):
            return await ctx.send("Utilise `!automod on` ou `!automod off`.")
        await database.update_setting(ctx.guild.id, "automod_enabled", state.lower() == "on")
        await ctx.send(f"✅ Automod {'activé' if state.lower() == 'on' else 'désactivé'}.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def addbannedword(self, ctx: commands.Context, *, word: str):
        await database.add_banned_word(ctx.guild.id, word)
        await ctx.send(f"✅ Mot ajouté à la liste des mots interdits.")
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def removebannedword(self, ctx: commands.Context, *, word: str):
        await database.remove_banned_word(ctx.guild.id, word)
        await ctx.send(f"✅ Mot retiré de la liste des mots interdits.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def bannedwords(self, ctx: commands.Context):
        words = await database.get_banned_words(ctx.guild.id)
        if not words:
            return await ctx.send("Aucun mot interdit configuré.")
        try:
            await ctx.author.send("Mots interdits sur ce serveur :\n" + ", ".join(f"`{w}`" for w in words))
            await ctx.send("📬 Je t'ai envoyé la liste en message privé.")
        except discord.Forbidden:
            await ctx.send("Active tes MP pour que je puisse t'envoyer la liste.")


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
