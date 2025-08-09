import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import logging

class Daily(commands.Cog):
    """
    Daily gold reward system for The Cavern's economy.
    
    Allows users to claim daily gold rewards with streak bonuses.
    Higher streaks provide more gold, encouraging consistent daily participation.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Daily rewards system loaded successfully")

    @app_commands.command(name="daily", description="Claim your daily gold!")
    async def daily(self, interaction: discord.Interaction):
        """
        Allow users to claim their daily gold reward with streak bonuses.
        
        Rewards increase with consecutive daily claims up to a maximum.
        Resets at midnight and tracks streak continuation.
        """
        self.logger.info("Daily reward claim by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            user_id = interaction.user.id
            guild_id = interaction.guild.id

            # Check if user is eligible for daily reward
            if self.bot.db.can_claim_daily(guild_id, user_id):
                # Handle streak calculation
                can_increase_streak = self.bot.db.can_increase_streak(guild_id, user_id)
                if can_increase_streak:
                    self.bot.db.increase_streak(guild_id, user_id)
                
                # Calculate reward based on streak (max reward at 5+ days)
                streak = self.bot.db.get_streak(guild_id, user_id)
                if streak >= 5:
                    reward = 150  # Maximum reward for 5+ day streaks
                else:
                    reward = 100 + 10 * streak  # Base 100 + 10 per streak day

                # Process the daily claim
                self.bot.db.claim_daily(guild_id, user_id)
                self.bot.db.add_gold(guild_id, user_id, reward)

                # Get updated balance for display
                gold = self.bot.db.get_user(guild_id, user_id)['gold']

                # Create reward notification embed
                embed = discord.Embed(
                    title="Daily Gold Claimed!", 
                    description=f"You claimed **{reward}** gold!",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Balance", 
                    value=f"You now have **{gold}** gold!", 
                    inline=False
                )
                embed.add_field(
                    name="Streak", 
                    value=f"You have claimed your daily gold **{streak}** days in a row", 
                    inline=False
                )
                embed.timestamp = datetime.now()

                await interaction.response.send_message(embed=embed)

            else:
                # User has already claimed today
                await interaction.response.send_message(
                    "You have already claimed your daily gold! Come back after midnight.", 
                    ephemeral=True
                )
        except Exception as e:
            self.logger.exception("Error occurred while processing daily command for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while claiming your daily gold. Please try again later.", ephemeral=True)

async def setup(bot):
    """Load the Daily cog into the bot."""
    await bot.add_cog(Daily(bot))