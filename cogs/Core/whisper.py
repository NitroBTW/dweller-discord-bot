import discord
from discord import app_commands
from discord.ext import commands
import logging

class Whisper(commands.Cog):
    """
    Anonymous messaging system for The Cavern.
    
    Allows users to send completely anonymous messages to a designated
    whisper channel, creating a safe and fun space for anonymous communication.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Whisper cog loaded successfully")

    @app_commands.command(name="whisper", description="Send an anonymous message.")
    @app_commands.describe(message="What is your whisper?")
    async def whisper(self, interaction: discord.Interaction, message: str):
        """
        Send an anonymous message to the whisper channel.
        
        Messages are completely anonymous - even bot developers cannot
        trace who sent what whisper, ensuring true anonymity.
        """
        self.logger.info("Whisper command used by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            guild = interaction.guild
            guild_id = guild.id

            # Get the configured whisper channel ID
            channel_id = self.bot.db.get_whisper_channel(guild_id)

            # Verify whisper channel is configured
            if not channel_id:
                self.logger.warning("No whisper channel configured for guild %s (ID: %s)", guild.name, guild_id)
                await interaction.response.send_message(f"It seems there is no whisper channel in {guild.name}")
                return

            # Get the actual channel object
            channel = guild.get_channel(int(channel_id))

            # Verify channel exists and is accessible
            if not channel:
                self.logger.warning("Could not find channel with ID: %s in guild: %s (ID: %s)", channel_id, guild.name, guild_id)
                await interaction.response.send_message(f"I could not fetch the whisper channel in {guild.name}")
                return

            # Create the anonymous whisper embed
            embed = discord.Embed(
                title="A whisper was heard through the Cavern!",
                description=f"{message}",
                color=discord.Color.random()
            )
            embed.set_footer(text="Whispers are completely anonymous, even to the dev!")

            # Send the whisper to the channel
            await channel.send(embed=embed)
            await interaction.response.send_message("We sent your message in the whisper channel.", ephemeral=True)
        except Exception as e:
            self.logger.exception("Error occurred while processing whisper command for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while sending your whisper. Please try again later.", ephemeral=True)

async def setup(bot):
    """Load the Whisper cog into the bot."""
    await bot.add_cog(Whisper(bot))