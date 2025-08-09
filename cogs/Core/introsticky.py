import discord
from discord.ext import commands
from discord import app_commands
import logging

# Template message for introductions channel
sticky_template = (
    "**Introduce Yourself!**\n"
    "Please use this template:\n"
    "Name/Nickname - \n"
    "Age - \n"
    "Pronouns - \n"
    "Hobbies - \n"
    "Likes - \n"
    "Dislikes - \n"
    "Extra Facts - \n"
)

class IntroSticky(commands.Cog):
    """
    Introduction channel sticky message system for The Cavern.
    
    Maintains a persistent template message at the bottom of the
    introductions channel to guide new members on how to introduce themselves.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Intro sticky system loaded successfully")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Maintain sticky template message in introductions channel.
        
        When a message is sent in the configured intros channel, deletes the
        previous template message and posts a new one to keep it at the bottom.
        """
        self.logger.info("Processing message for intro sticky in guild_id=%s, user_id=%s", getattr(message.guild, 'id', None), getattr(message.author, 'id', None))
        try:
            # Skip bot messages and DMs
            if message.author.bot or not message.guild:
                return

            guild = message.guild
            guild_id = message.guild.id

            # Check if this guild has an intros channel configured
            channel_id = self.bot.db.get_intros_channel(guild_id)

            if not channel_id:
                self.logger.warning("No intros channel set for guild %s", guild.name)
                return
        
            # Only process messages in the designated intros channel
            if str(message.channel.id) != str(channel_id):
                return
        
            # Verify the intros channel still exists
            channel = guild.get_channel(int(channel_id))
            if channel is None:
                self.logger.warning("Intro channel not found (ID: %s) in %s", channel_id, guild.name)
                return

            # Handle sticky message rotation
            last_sticky_id = self.bot.db.get_intro_id(guild_id)

            if last_sticky_id is None:
                # No previous sticky message, create the first one
                self.logger.info("Creating first sticky message for intro channel in %s", guild.name)
                sticky = await channel.send(sticky_template)
                self.bot.db.set_intro_id(guild_id, sticky.id)
            else:
                # Delete the previous sticky message if it exists
                try:
                    last_message = await message.channel.fetch_message(int(last_sticky_id))
                    await last_message.delete()
                except (discord.NotFound, discord.Forbidden):
                    pass  # Message already deleted or can't be deleted
        
                # Post new sticky message at the bottom
                sticky = await message.channel.send(sticky_template)
                self.bot.db.set_intro_id(guild_id, sticky.id)
        except Exception as e:
            self.logger.exception("Error handling intro sticky message event in guild_id=%s, user_id=%s", getattr(message.guild, 'id', None), getattr(message.author, 'id', None))


async def setup(bot):
    """Load the IntroSticky cog into the bot."""
    await bot.add_cog(IntroSticky(bot))
