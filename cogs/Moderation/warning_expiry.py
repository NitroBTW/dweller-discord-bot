import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime, timedelta

class WarningExpiry(commands.Cog):
    """
    Automatic warning expiry system for The Cavern.
    
    Runs daily checks to automatically remove warnings older than 30 days,
    helping maintain fair moderation with time-based forgiveness.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Warning expiry system loaded successfully")
        # Start the automated daily warning expiry task
        self.check_warning_expiry.start()

    def cog_unload(self):
        # Stop the task when the cog is unloaded
        self.check_warning_expiry.cancel()

    @tasks.loop(hours=24)  # Run every 24 hours
    async def check_warning_expiry(self):
        """Check for and remove warnings older than 30 days"""
        self.logger.info("Starting daily warning expiry check")
        
        try:
            # Get current time for comparison
            current_time = datetime.now()
            expiry_threshold = current_time - timedelta(days=30)
            
            # Track statistics
            total_expired = 0
            guilds_checked = 0
            
            # Check all guilds in the database
            for guild_id_str in self.bot.db.data:
                guild_id = int(guild_id_str)
                guild = self.bot.db.get_guild(guild_id)
                guilds_checked += 1
                
                # Check each user in the guild
                for user_id_str in guild.get("users", {}):
                    user_id = int(user_id_str)
                    user_data = guild["users"][user_id_str]
                    warnings = user_data.get("warnings", [])
                    
                    if not warnings:
                        continue
                    
                    # Filter out expired warnings
                    original_count = len(warnings)
                    valid_warnings = []
                    
                    for warning in warnings:
                        try:
                            warning_time = datetime.fromisoformat(warning.get("timestamp", ""))
                            if warning_time > expiry_threshold:
                                valid_warnings.append(warning)
                        except (ValueError, TypeError):
                            # If timestamp is invalid, keep the warning for now
                            valid_warnings.append(warning)
                    
                    # Update warnings if any were removed
                    if len(valid_warnings) < original_count:
                        expired_count = original_count - len(valid_warnings)
                        total_expired += expired_count
                        
                        # Update the user's warnings in the database
                        user_data["warnings"] = valid_warnings
                        self.logger.info(f"Removed {expired_count} expired warnings from user {user_id} in guild {guild_id}")
            
            # Save the database after all changes
            self.bot.db._save_database()
            
            self.logger.info(f"Warning expiry check completed. Checked {guilds_checked} guilds, removed {total_expired} expired warnings")
            
        except Exception as e:
            self.logger.exception("Error occurred during warning expiry check")

    @check_warning_expiry.before_loop
    async def before_check_warning_expiry(self):
        """Wait until the bot is ready before starting the task"""
        await self.bot.wait_until_ready()

    @check_warning_expiry.error
    async def check_warning_expiry_error(self, error):
        """Handle errors in the warning expiry task"""
        self.logger.exception("Error in warning expiry task")

async def setup(bot):
    """Load the WarningExpiry cog into the bot."""
    await bot.add_cog(WarningExpiry(bot)) 