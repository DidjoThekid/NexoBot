import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"NexoBot connecté en tant que {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong !")

bot.run(TOKEN)
