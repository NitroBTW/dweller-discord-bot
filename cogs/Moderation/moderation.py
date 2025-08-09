import discord
from discord import app_commands
from discord.ext import commands
import logging
from datetime import datetime

class Moderation(commands.Cog):
    """
    Moderation tools and user data management for The Cavern.
    
    Provides admin commands for managing user data, issuing warnings,
    and performing various moderation tasks.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Moderation system loaded successfully")


    # Set a user's data
    @app_commands.command(name="set_user_data", description="Set a user's data (Staff only)")
    @app_commands.describe(type="The type of data you want to set for the user", value="The new value for this data")
    @app_commands.choices(
        type=[
            app_commands.Choice(name="Tier (int)", value="tier"),
            app_commands.Choice(name="Gold (int)", value="gold"),
            app_commands.Choice(name="Roulette wins (int)", value="roulette_wins"),
            app_commands.Choice(name="Roulette losses (int)", value="roulette_losses"),
            app_commands.Choice(name="Blackjack wins (int)", value="blackjack_wins"),
            app_commands.Choice(name="Blackjack losses (int)", value="blackjack_losses"),
            app_commands.Choice(name="Slots wins (int)", value="slots_wins"),
            app_commands.Choice(name="Slots losses (int)", value="slots_losses"),
            app_commands.Choice(name="Last daily claim (None/iso format string)", value="last_daily_claim"),
            app_commands.Choice(name="Streak (int)", value="streak"),
            app_commands.Choice(name="Mimic Expiry (None/iso format string)", value="mimic_expiry"),
            app_commands.Choice(name="Barrel Expiry (None/iso format string)", value="barrel_expiry"),
        ]
    )
    async def set_user_data(self, interaction: discord.Interaction, user: discord.Member, type: str, value: str):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to set data for user_id=%s", interaction.user.id, interaction.guild.id, user.id)
        try:
            # Update the user's data
            self.bot.db.set_user_data(interaction.guild.id, user.id, type, value)
            
            # Send confirmation message
            await interaction.response.send_message(f"Set {user.mention}'s {type} to {value}", ephemeral=True)
        except Exception as e:
            self.logger.exception("Error occurred while setting data for user_id=%s in guild_id=%s", user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while setting the user's data. Please try again later.", ephemeral=True)


    # Get a user's data
    @app_commands.command(name="get_user_data", description="Get a user's data (Staff only)")
    async def get_user_data(self, interaction: discord.Interaction, user: discord.Member):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to get data for user_id=%s", interaction.user.id, interaction.guild.id, user.id)
        try:
            # Get user data from the database
            if user.bot:
                await interaction.response.send_message(content=f"Bots' data is not stored to the database")
                return
            
            user_data = self.bot.db.get_user(interaction.guild.id, user.id)

            # Create the empty embed
            embed = discord.Embed(
                title=f"User Data for {user.name}",
                color=discord.Color.red()
            )

            # Get the key value pairs and add fields
            for key, value in user_data.items():
                embed.add_field(name=key.replace('_', ' ').title(), value=str(value), inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            self.logger.exception("Error occurred while getting user data for user_id=%s in guild_id=%s", user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while fetching the user's data. Please try again later.", ephemeral=True)

    # Warn a user
    @app_commands.command(name="warn", description="Add a warning to a user (Staff Only)")
    @app_commands.describe(user="The user to warn", reason="The reason for the warning")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to warn user_id=%s", interaction.user.id, interaction.guild.id, user.id)
        try:
            # Get the user from the database
            if user.bot:
                await interaction.response.send_message(content=f"You cannot warn a bot.", ephemeral=True)
                return
            
            # Add a warning to the user
            self.bot.db.add_warning(interaction.guild.id, user.id, reason)

            # Get the user's warning count
            warning_count = self.bot.db.get_warning_count(interaction.guild.id, user.id)

            # Respond to the command
            await interaction.response.send_message(content=f"Successfully added a warning to {user.mention}, they now have {warning_count} warnings.\n**Reason:** {reason}")
        
        except Exception as e:
            self.logger.exception("Error occurred while adding a warning to user_id=%s in guild_id=%s", user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while warning the user. Please try again later.", ephemeral=True)

    # Get a user's warnings
    @app_commands.command(name="warnings", description="Get a user's warnings (Staff only)")
    async def get_warnings(self, interaction: discord.Interaction, user: discord.Member):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to get warnings for user_id=%s", interaction.user.id, interaction.guild.id, user.id)
        try:
            if user.bot:
                await interaction.response.send_message(content=f"Bots don't have warnings.", ephemeral=True)
                return
            
            warnings = self.bot.db.get_warnings(interaction.guild.id, user.id)
            
            if not warnings:
                await interaction.response.send_message(f"{user.mention} has no warnings.", ephemeral=True)
                return
            
            # Create embed with warnings
            embed = discord.Embed(
                title=f"Warnings for {user.name}",
                description=f"Total warnings: {len(warnings)}",
                color=discord.Color.red()
            )
            
            for i, warning in enumerate(warnings, 1):
                timestamp = warning.get("timestamp", "Unknown")
                reason = warning.get("reason", "No reason provided")
                # Format timestamp for display
                try:
                    dt = datetime.fromisoformat(timestamp)
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_time = timestamp
                
                embed.add_field(
                    name=f"Warning #{i}",
                    value=f"**Reason:** {reason}\n**Date:** {formatted_time}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.exception("Error occurred while getting warnings for user_id=%s in guild_id=%s", user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while fetching the user's warnings. Please try again later.", ephemeral=True)

async def setup(bot):
    """Load the Moderation cog into the bot."""
    await bot.add_cog(Moderation(bot))