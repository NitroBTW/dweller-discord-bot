import discord
from discord.ext import commands
from datetime import datetime
import logging

class BarrelTimeListener(commands.Cog):
    """
    Barrel Time effect monitoring for The Cavern's shop system.
    
    Automatically deletes messages from users who are currently
    "in the barrel" - a temporary muting effect from the shop.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Barrel Time system loaded successfully")

    @commands.Cog.listener()
    async def on_message(self, message):
        self.logger.info("Message event in guild_id=%s, user_id=%s", getattr(message.guild, 'id', None), getattr(message.author, 'id', None))
        try:
            # Dont respond to dms or bots
            if message.author.bot or not message.guild:
                return

            # Get the guild ID and user ID of the message
            guild_id = message.guild.id
            user_id = message.author.id

            # Get the user from the guild
            barrel_expiry = self.bot.db.get_barrel_expiry(guild_id, user_id)
            if barrel_expiry:
                expiry_time = datetime.fromisoformat(barrel_expiry)
                # Check if the user is still in the barrel
                if expiry_time > datetime.utcnow():
                    await message.delete()
                    return
        except Exception as e:
            self.logger.exception("Error handling message event in guild_id=%s, user_id=%s", getattr(message.guild, 'id', None), getattr(message.author, 'id', None))
    




async def setup(bot):
    """Load the BarrelTimeListener cog into the bot."""
    await bot.add_cog(BarrelTimeListener(bot))