import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class TierListener(commands.Cog):
    """
    User tier and activity tracking system for The Cavern.
    
    Monitors user message activity and automatically promotes users to higher
    tiers based on message count thresholds, assigning appropriate roles.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Tier system cog loaded successfully")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Track user messages and handle tier upgrades.
        
        Increments user message count and checks for tier promotion eligibility.
        Upgrades users at 100 messages (tier 2) and 1000 messages (tier 3).
        """
        self.logger.info("Processing message for tier tracking in guild_id=%s, user_id=%s", getattr(message.guild, 'id', None), getattr(message.author, 'id', None))
        try:
            # Skip bot messages and DMs
            if message.author.bot or not message.guild:
                return

            guild_id = message.guild.id
            user_id = message.author.id
            self.logger.info(f"Tracking message from {message.author.name} in {message.guild.name}")

            # Get the general channel for tier upgrade announcements
            channel_id = self.bot.db.get_general_channel(guild_id)
            self.logger.info(f"General channel ID: {channel_id}")
            channel = self.bot.get_channel(int(channel_id)) if channel_id else None
            self.logger.info(f"General channel found: {channel is not None}")

            # Ensure user exists in database and increment message count
            user = self.bot.db.get_user(guild_id, user_id)
            self.bot.db.add_messages(guild_id, user_id, 1)

            # Get updated stats for tier checking
            message_count = self.bot.db.get_messages(guild_id, user_id)
            tier = self.bot.db.get_tier(guild_id, user_id)
            self.logger.info(f"User {message.author.name}: {message_count} messages, tier {tier}")

            # Check for tier 2 upgrade (100 messages)
            if message_count >= 100 and tier == 1:
                self.logger.info(f"Upgrading {message.author.name} to tier 2")
                
                # Update user tier in database
                self.bot.db.set_tier(guild_id, user_id, 2)

                # Get and validate tier 2 role
                role_id = self.bot.db.get_tier_role(guild_id, 2)
                self.logger.info(f"Tier 2 role ID: {role_id}")
                if role_id is None:
                    self.logger.warning(f"No tier 2 role set for guild {guild_id}")
                    return
                role = message.guild.get_role(int(role_id))
                if role is None:
                    self.logger.warning(f"Tier 2 role with ID {role_id} not found in guild {guild_id}")
                    return

                # Assign the tier role to the user
                try:
                    await message.author.add_roles(role, reason="Tier 2 upgrade")
                except Exception as e:
                    self.logger.error(f"Failed to add tier 2 role: {e}")

                # Create tier upgrade celebration embed
                embed = discord.Embed(
                    title=f"Thanks for drinking with us {message.author.name}!",
                    color=discord.Color.dark_teal()
                )
                embed.add_field(name="You reached a new tier", value=f"{role.mention}")

                # Send celebration message in general channel
                self.logger.info(f"Attempting to send tier 2 embed to channel: {channel}")
                if channel is None:
                    self.logger.warning(f"General channel not set or not found for guild {guild_id}")
                    return
                await channel.send(content=f"{message.author.mention}", embed=embed)
                self.logger.info(f"Tier 2 upgrade announced successfully")

            # Check for tier 3 upgrade (1000 messages)  
            elif message_count >= 1000 and tier == 2:
                self.logger.info(f"Upgrading {message.author.name} to tier 3")
                
                # Update user tier in database
                self.bot.db.set_tier(guild_id, user_id, 3)

                # Get and validate tier 3 role
                role_id = self.bot.db.get_tier_role(guild_id, 3)
                self.logger.info(f"Tier 3 role ID: {role_id}")
                if role_id is None:
                    self.logger.warning(f"No tier 3 role set for guild {guild_id}")
                    return
                role = message.guild.get_role(int(role_id))
                if role is None:
                    self.logger.warning(f"Tier 3 role with ID {role_id} not found in guild {guild_id}")
                    return

                # Assign the tier role to the user
                try:
                    await message.author.add_roles(role, reason="Tier 3 upgrade")
                except Exception as e:
                    self.logger.error(f"Failed to add tier 3 role: {e}")

                # Create tier upgrade celebration embed for patrons
                embed = discord.Embed(
                    title=f"You're a patron {message.author.name}!",
                    color=discord.Color.dark_teal()
                )
                embed.add_field(name="You reached a new tier", value=f"{role.mention}")
                
                # Send celebration message in general channel
                self.logger.info(f"Attempting to send tier 3 embed to channel: {channel}")
                if channel is None:
                    self.logger.warning(f"General channel not set or not found for guild {guild_id}")
                    return
                await channel.send(content=f"{message.author.mention}", embed=embed)
                self.logger.info(f"Tier 3 upgrade announced successfully")
        except Exception as e:
            self.logger.exception("Error handling tier system message event in guild_id=%s, user_id=%s", getattr(message.guild, 'id', None), getattr(message.author, 'id', None))

async def setup(bot):
    """Load the TierListener cog into the bot."""
    await bot.add_cog(TierListener(bot))
