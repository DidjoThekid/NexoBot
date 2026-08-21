import discord
from discord.ext import commands
from discord.ext.commands import Cog, command
import logging
import asyncio

logger = logging.getLogger("NexoBot")

class Tickets(Cog):
    """Système de tickets de support"""
    
    def __init__(self, bot):
        self.bot = bot
        self.open_tickets = {}
    
    @command(name="ticket")
    async def ticket(self, ctx, *, reason: str = "Aucune raison fournie"):
        """Ouvre un ticket de support"""
        guild = ctx.guild
        author = ctx.author
        
        # Vérifier si l'utilisateur a déjà un ticket ouvert
        if author.id in self.open_tickets:
            await ctx.send("❌ Tu as déjà un ticket ouvert !")
            return
        
        # Créer un nouveau canal de ticket
        ticket_number = len(self.open_tickets) + 1
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{ticket_number:03d}",
            category=self._get_ticket_category(guild),
            reason=f"Ticket créé par {author}"
        )
        
        # Configurer les permissions
        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = True
        overwrite.send_messages = True
        await ticket_channel.set_permissions(author, overwrite=overwrite)
        
        # Envoyer le message d'accueil
        embed = discord.Embed(
            title="🎫 Ticket de support",
            description=f"Bienvenue dans ton ticket, {author.mention} !",
            color=discord.Color.blue()
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.add_field(
            name="Instructions",
            value="• Décris ton problème en détail\n• Un membre du support te répondra bientôt\n• Utilise `!close` pour fermer le ticket",
            inline=False
        )
        embed.set_footer(text=f"Ticket #{ticket_number}")
        
        await ticket_channel.send(embed=embed)
        await ticket_channel.send(f"{author.mention}, ton ticket a été créé !")
        
        # Enregistrer le ticket
        self.open_tickets[author.id] = ticket_channel.id
        
        await ctx.send(f"✅ Ticket créé : {ticket_channel.mention}", delete_after=5)
        logger.info(f"Ticket #{ticket_number} créé par {author}")
    
    @command(name="close")
    @commands.has_permissions(manage_channels=True)
    async def close(self, ctx):
        """Ferme le ticket actuel"""
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ Cette commande ne peut être utilisée que dans un ticket.")
            return
        
        # Confirmer la fermeture
        confirm_embed = discord.Embed(
            title="🔒 Fermeture du ticket",
            description="Le ticket va être fermé dans 5 secondes...",
            color=discord.Color.orange()
        )
        msg = await ctx.send(embed=confirm_embed)
        await asyncio.sleep(5)
        
        # Supprimer le canal
        await ctx.channel.delete(reason="Ticket fermé")
        logger.info(f"Ticket {ctx.channel.name} fermé par {ctx.author}")
    
    def _get_ticket_category(self, guild):
        """Récupère la catégorie des tickets"""
        for category in guild.categories:
            if "ticket" in category.name.lower():
                return category
        return None

def setup(bot):
    bot.add_cog(Tickets(bot))
