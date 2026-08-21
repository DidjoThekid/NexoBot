import discord
from discord.ext import commands
from discord.ext.commands import Cog, command
import logging
import asyncio

logger = logging.getLogger("NexoBot")

class Tickets(Cog):
    """Système de tickets"""
    
    def __init__(self, bot):
        self.bot = bot
        self.open_tickets = {}
    
    @command(name="ticket")
    async def ticket(self, ctx, *, reason: str = "Aucune raison"):
        guild = ctx.guild
        author = ctx.author
        
        if author.id in self.open_tickets:
            await ctx.send("❌ Tu as déjà un ticket ouvert !")
            return
        
        ticket_number = len(self.open_tickets) + 1
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{ticket_number:03d}",
            reason=f"Ticket créé par {author}"
        )
        
        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = True
        overwrite.send_messages = True
        await ticket_channel.set_permissions(author, overwrite=overwrite)
        
        embed = discord.Embed(
            title=" Ticket de support",
            description=f"Bienvenue {author.mention} !",
            color=discord.Color.blue()
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.add_field(name="Utilise", value="`!close` pour fermer", inline=False)
        
        await ticket_channel.send(embed=embed)
        self.open_tickets[author.id] = ticket_channel.id
        
        await ctx.send(f"✅ Ticket créé : {ticket_channel.mention}", delete_after=5)
    
    @command(name="close")
    async def close(self, ctx):
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ Cette commande ne fonctionne que dans un ticket.")
            return
        
        await ctx.send("🔒 Le ticket va être fermé dans 5 secondes...")
        await asyncio.sleep(5)
        await ctx.channel.delete()

async def setup(bot):
    await bot.add_cog(Tickets(bot))
