import discord, asyncio, logging
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class Bump(commands.Cog):
    """
    Server bump reminder system for The Cavern.
    
    Monitors for Disboard bump completions and automatically schedules
    reminder messages to help maintain server visibility and growth.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Bump reminder system loaded successfully")
        self.reminder_tasks = {}  # Track active reminder tasks per guild 

    async def bump_reminder_after_delay(self, guild_id):
        """
        Send a bump reminder after the 2-hour cooldown period.
        
        Waits exactly 2 hours (7200 seconds) then sends a reminder
        to the configured bump role in the bot channel.
        """
        await asyncio.sleep(7200)  # Wait 2 hours for bump cooldown
        guild = self.bot.get_guild(guild_id)

        # Verify guild still exists
        if not guild:
            self.logger.warning("Guild %s not found for bump reminder.", guild_id)
            return

        # Get and validate bump role configuration
        bump_role_id = self.bot.db.get_bump_role(guild_id)  
        if not bump_role_id:
            self.logger.info("No bump role set for guild %s", guild.name) 
            return

        bump_role = guild.get_role(int(bump_role_id))  
        if not bump_role:
            self.logger.warning("Bump role not found in guild %s", guild.name)
            return

        # Get and validate bot channel configuration
        bot_channel_id = self.bot.db.get_bot_channel(guild_id)  
        if not bot_channel_id:
            self.logger.info("No bot channel set for guild %s", guild.name) 
            return

        channel = guild.get_channel(int(bot_channel_id))  
        if not channel:
            self.logger.warning("Bot channel not found in guild %s", guild.name)
            return

        # Create themed bump reminder embed
        embed = discord.Embed(
            title="Bump Reminder!",
            description="It's time to bump the server!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="How to bump:",
            value="Use `/bump` to bump the server and help grow the Cavern's reach!",
            inline=False
        )
        embed.timestamp = datetime.utcnow()

        # Send the reminder to the configured channel
        try:
            await channel.send(content=f"{bump_role.mention}", embed=embed)
            self.logger.info("Sent bump reminder to %s in #%s", guild.name, channel.name)
        except discord.Forbidden:
            self.logger.warning("Cannot send messages in %s #%s", guild.name, channel.name)
        except Exception as e:
            self.logger.exception("Error sending bump reminder to %s: %s", guild.name, e)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Monitor for Disboard bump completions and schedule reminders.
        
        Detects when the Disboard bot confirms a bump and automatically
        schedules a reminder for the next available bump time.
        """
        # Only process messages from the Disboard bot
        if message.author.id != 302050872383242240:
            return
            
        # Check for bump completion confirmation
        if message.embeds:
            embed = message.embeds[0]
            if embed.description and "Bump done!" in embed.description:
                try:
                    # Send thank you message to acknowledge the bump
                    thank_embed = discord.Embed(
                        title="Thank you for bumping!",
                        description=f"We will remind you once you can bump again!",
                        color=discord.Color.gold()
                    )
                    await message.channel.send(embed=thank_embed)
                    self.logger.info("Detected bump, sent thank you message.")  

                except Exception as e:
                    self.logger.exception("Error sending thank you message after bump: %s", e)

                # Manage reminder scheduling for this guild
                guild_id = message.guild.id 
                
                # Cancel any existing reminder task for this guild
                if guild_id in self.reminder_tasks:
                    task = self.reminder_tasks[guild_id]  
                    if not task.done():
                        task.cancel()  
                        self.logger.info("Cancelled previous bump reminder for guild %s", guild_id)
            
                # Schedule a new reminder task for this guild
                self.reminder_tasks[guild_id] = asyncio.create_task(self.bump_reminder_after_delay(guild_id))
                self.logger.info("Scheduled new bump reminder for guild %s in 2 hours.", guild_id)

async def setup(bot):
    """Load the Bump cog into the bot."""
    await bot.add_cog(Bump(bot))
