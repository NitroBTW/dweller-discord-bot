import discord
from discord import app_commands
from discord.ext import commands
import logging

class Balance(commands.Cog):
    """
    Economy cog for checking user gold balance.
    
    Provides a simple slash command to display how much gold
    a user has earned through the bot's economy system.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Successfully loaded cog")

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        """Check the user's current gold balance and display it in an embed."""
        self.logger.info("Command invoked by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            # Get the user and guild IDs
            user_id = interaction.user.id
            guild_id = interaction.guild.id

            # Get the user's gold
            gold = self.bot.db.get_user_gold(guild_id, user_id)

            # Create an embed to send to the user
            embed = discord.Embed(
                title="Balance", 
                description=f"You have **{gold}** gold.", 
                color=discord.Color.green()
                )

            # Send the balance information to the user
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            self.logger.exception("Error occurred while checking balance for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while checking your balance. Please try again later.", ephemeral=True)

async def setup(bot):
    """Load the Balance cog into the bot."""
    await bot.add_cog(Balance(bot))