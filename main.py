import asyncio
import logging
import os

import discord
from discord import app_commands
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
intents.message_content = True  # requis pour l'automod (lecture du contenu des messages)

# Le préfixe texte n'est plus utilisé (tout passe en slash commands), mais
# discord.py exige quand même un command_prefix pour instancier un Bot.
bot = commands.Bot(command_prefix="!", intents=intents)

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

    try:
        synced = await bot.tree.sync()
        logger.info(f"{len(synced)} slash commande(s) synchronisée(s) globalement.")
    except Exception:
        logger.exception("Échec de la synchronisation des slash commands.")


@bot.event
async def on_guild_join(guild: discord.Guild):
    logger.info(f"Rejoint un nouveau serveur : {guild.name} (ID: {guild.id})")
    await update_status()


@bot.event
async def on_guild_remove(guild: discord.Guild):
    logger.info(f"Retiré du serveur : {guild.name} (ID: {guild.id})")
    await update_status()


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Gestion centralisée des erreurs de slash commands."""
    if isinstance(error, app_commands.MissingPermissions):
        message = "🚫 Tu n'as pas la permission d'utiliser cette commande."
    elif isinstance(error, app_commands.BotMissingPermissions):
        message = "⚠️ Il me manque des permissions pour faire ça."
    elif isinstance(error, app_commands.CommandOnCooldown):
        message = f"⏳ Attends encore {error.retry_after:.1f}s avant de réessayer."
    else:
        logger.exception("Erreur non gérée sur une slash command", exc_info=error)
        message = "💥 Une erreur inattendue est survenue."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


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
