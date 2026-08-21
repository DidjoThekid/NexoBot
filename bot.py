"""
NexoBot - Votre serveur, simplifié.
"""

import os
import asyncio
import logging
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Récupération du token
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError(
        "DISCORD_TOKEN manquant. Copie .env.example en .env et renseigne ton token."
    )

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("NexoBot")

# Chargement de la configuration
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

# Configuration des intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

# Création du bot
bot = commands.Bot(
    command_prefix=CONFIG.get("prefix", "!"),
    intents=intents,
    help_command=commands.DefaultHelpCommand(),
    description="NexoBot - Simplifiez la gestion de votre serveur Discord"
)

# Rend la config accessible depuis tous les cogs
bot.config = CONFIG

# Liste des cogs à charger
COGS = [
    "cogs.moderation",
    "cogs.tickets",
    "cogs.logs",
    "cogs.welcome",
    "cogs.utility",
]

@bot.event
async def on_ready():
    """Exécuté quand le bot est connecté"""
    logger.info(f"NexoBot connecté en tant que {bot.user} (ID: {bot.user.id})")
    logger.info(f"Présent sur {len(bot.guilds)} serveur(s).")
    logger.info(f"{len(bot.users)} utilisateur(s) total(aux).")
    
    # Changement du statut
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} serveurs"
        )
    )

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Gestion centralisée des erreurs de commandes."""
    if isinstance(error, commands.CommandNotFound):
        return  # on ignore silencieusement les commandes inconnues

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(" Tu n'as pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("️ Il me manque des permissions pour faire ça.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❗ Argument manquant : `{error.param.name}`.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❗ Argument invalide. Vérifie ta commande.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f" Attends encore {error.retry_after:.1f}s avant de réessayer.")
    else:
        logger.exception("Erreur non gérée", exc_info=error)
        await ctx.send(" Une erreur inattendue est survenue.")

async def main():
    """Fonction principale de démarrage"""
    async with bot:
        # Chargement des cogs
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                logger.info(f"✓ Cog chargé : {cog}")
            except Exception as e:
                logger.error(f"✗ Échec du chargement du cog : {cog}")
                logger.error(f"  Erreur: {e}")
        
        # Démarrage du bot
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
