import discord
from discord.ext import commands
import logging
import asyncio

class JoinLeaveListener(commands.Cog):
    """
    Welcome and goodbye system for The Cavern.
    
    Handles member join/leave events with themed messages, automatic
    user database creation, and delayed welcome messages with server guidance.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Join/Leave listener cog loaded successfully")

    @commands.Cog.listener()
    async def on_member_join(self, user):
        """
        Handle new member joining The Cavern.
        
        Sends a themed welcome message, creates user database entry,
        and provides a delayed guidance message in the general channel.
        """
        self.logger.info("New member joined: user_id=%s in guild_id=%s", user.id, user.guild.id)
        try:
            guild = user.guild
            guild_id = guild.id
            user_id = user.id

            # Get user's avatar for the welcome message
            user_pfp = user.avatar.url if user.avatar else user.default_avatar.url

            # Create themed welcome embed
            embed = discord.Embed(
                title=f"Welcome in to the Cavern, {user.display_name}!",
                description=f"Grab a drink or get out!",
                color=discord.Color.random()
            )
            embed.set_thumbnail(url=user_pfp)

            # Try to send welcome message to configured welcome channel
            channel_id = self.bot.db.get_welcome_channel(guild_id)

            if not channel_id:
                self.logger.warning("No welcome channel configured for %s", guild.name)
            else:
                channel = guild.get_channel(int(channel_id))
                if channel is None:
                    self.logger.warning("Welcome channel not found (ID: %s) in %s", channel_id, guild.name)
                else:
                    try:
                        await channel.send(content=user.mention, embed=embed)
                    except discord.Forbidden:
                        self.logger.warning("Missing permissions in #%s in %s", channel.name, guild.name)
                    except discord.HTTPException as e:
                        self.logger.error("Failed to send to welcome channel in %s: %s", guild.name, e)
        
            # Create user database entry for new members (skip bots)
            if not user.bot:
                self.bot.db.get_user(guild_id, user_id)

            # Send delayed guidance message in general channel for new members
            if not user.bot:
                await asyncio.sleep(30)  # Wait 30 seconds before guidance message
                
                # Get channel IDs for mentions
                general_channel_id = self.bot.db.get_general_channel(guild_id)
                intros_channel_id = self.bot.db.get_intros_channel(guild_id)
                color_channel_id = self.bot.db.get_color_channel(guild_id)
                
                # Get the general channel object
                general_channel = guild.get_channel(int(general_channel_id)) if general_channel_id else None
                
                # Create channel mentions or fallback to generic names
                intros_mention = f'<#{intros_channel_id}>' if intros_channel_id else '#intros'
                color_mention = f'<#{color_channel_id}>' if color_channel_id else '#colors'
                
                if general_channel:
                    # Create guidance embed with server information
                    embed2 = discord.Embed(
                        title=f"Welcome to The Cavern {user.display_name}!",
                        color=discord.Color.random()
                    )
                    embed2.add_field(
                        name="Introduce yourself",
                        value=f"Head to {intros_mention} and tell us a bit about yourself",
                        inline=False
                    )
                    embed2.add_field(
                        name="Decorate your profile",
                        value=f"Go and grab a `/color` for your name in {color_mention}",
                        inline=False
                    )
                    embed2.add_field(
                        name="Grow your wealth",
                        value="The Cavern operates a gold based economy. Get your `/daily` reward streak going and checkout what we have in the `/shop`, (or gamble it away with `/games`)",
                        inline=False
                    )
                    try:
                        await general_channel.send(content=user.mention, embed=embed2)
                    except Exception as e:
                        self.logger.warning("Failed to send delayed general welcome: %s", e)
        except Exception as e:
            self.logger.exception("Error handling member join for user_id=%s in guild_id=%s", user.id, getattr(user.guild, 'id', None))

    @commands.Cog.listener()
    async def on_member_remove(self, user):
        """
        Handle member leaving The Cavern.
        
        Sends a themed goodbye message in the configured goodbye channel
        and ensures user data is preserved in the database.
        """
        self.logger.info("Member left: user_id=%s in guild_id=%s", user.id, user.guild.id)
        try:
            guild = user.guild
            guild_id = guild.id
            user_id = user.id

            # Get user's avatar for the goodbye message
            user_pfp = user.avatar.url if user.avatar else user.default_avatar.url

            # Create themed goodbye embed
            embed = discord.Embed(
                title=f"{user.display_name}, See you later traveller!",
                description=f"We hope you enjoyed your time with us!",
                color=discord.Color.random()
            )
            embed.set_thumbnail(url=user_pfp)

            # Try to send goodbye message to configured goodbye channel
            channel_id = self.bot.db.get_goodbye_channel(guild_id)

            if not channel_id:
                self.logger.warning("No goodbye channel configured for %s", guild.name)
            else:
                channel = guild.get_channel(int(channel_id))
                if channel is None:
                    self.logger.warning("Goodbye channel not found (ID: %s) in %s", channel_id, guild.name)
                else:
                    try:
                        await channel.send(embed=embed)
                    except discord.Forbidden:
                        self.logger.warning("Missing permissions in #%s in %s", channel.name, guild.name)
                    except discord.HTTPException as e:
                        self.logger.error("Failed to send to goodbye channel in %s: %s", guild.name, e)

            # Ensure user data exists in database (preserves data for possible return)
            if not user.bot:
                self.bot.db.get_user(guild_id, user_id)
        except Exception as e:
            self.logger.exception("Error handling member remove for user_id=%s in guild_id=%s", user.id, getattr(user.guild, 'id', None))


async def setup(bot):
    """Load the JoinLeaveListener cog into the bot."""
    await bot.add_cog(JoinLeaveListener(bot))