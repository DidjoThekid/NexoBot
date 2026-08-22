import asyncio
import logging
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import database

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError(
        "DISCORD_TOKEN manquant. Copie .env.example en .env et renseigne ton token."
    )

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("NexoBot")

# ---------------------------------------------------------------------------
# Intents & Bot
# ---------------------------------------------------------------------------

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # requis pour la modération / lecture des messages


async def get_prefix(bot: commands.Bot, message: discord.Message):
    """Préfixe dynamique : chaque serveur peut avoir le sien, stocké en base."""
    if not message.guild:
        return "!"
    settings = await database.get_settings(message.guild.id)
    return settings.get("prefix", "!")


bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=commands.DefaultHelpCommand(),
)

COGS = [
    "cogs.moderation",
    "cogs.tickets",
    "cogs.logs",
    "cogs.welcome",
    "cogs.utility",
    "cogs.settings",
    "cogs.automod",
]


@tasks.loop(minutes=10)
async def update_status():
    """Met à jour le statut du bot avec le nombre de serveurs, toutes les 10 minutes."""
    count = len(bot.guilds)
    label = "serveur" if count <= 1 else "serveurs"
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{count} {label} 👀",
        )
    )


@bot.event
async def on_ready():
    logger.info(f"NexoBot connecté en tant que {bot.user} (ID: {bot.user.id})")
    logger.info(f"Présent sur {len(bot.guilds)} serveur(s).")
    if not update_status.is_running():
        update_status.start()


@bot.event
async def on_guild_join(guild: discord.Guild):
    logger.info(f"Rejoint un nouveau serveur : {guild.name} (ID: {guild.id})")
    await update_status()  # mise à jour immédiate, pas besoin d'attendre 10 minutes


@bot.event
async def on_guild_remove(guild: discord.Guild):
    logger.info(f"Retiré du serveur : {guild.name} (ID: {guild.id})")
    await update_status()


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Gestion centralisée des erreurs de commandes."""
    if isinstance(error, commands.CommandNotFound):
        return  # on ignore silencieusement les commandes inconnues

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 Tu n'as pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("⚠️ Il me manque des permissions pour faire ça.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❗ Argument manquant : `{error.param.name}`.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❗ Argument invalide. Vérifie ta commande.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Attends encore {error.retry_after:.1f}s avant de réessayer.")
    else:
        logger.exception("Erreur non gérée", exc_info=error)
        await ctx.send("💥 Une erreur inattendue est survenue.")


async def main():
    await database.init_db()
    logger.info("Base de données PostgreSQL initialisée.")

    try:
        async with bot:
            for cog in COGS:
                try:
                    await bot.load_extension(cog)
                    logger.info(f"Cog chargé : {cog}")
                except Exception:
                    logger.exception(f"Échec du chargement du cog : {cog}")
            await bot.start(TOKEN)
    finally:
        await database.close_db()


if __name__ == "__main__":
    asyncio.run(main())
