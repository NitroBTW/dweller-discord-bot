import discord
import logging
from discord import app_commands
from discord.ext import commands

class SetupCog(commands.Cog):
    """
    Server configuration commands for The Cavern.
    
    Provides admin tools to configure bot channels, roles, and
    various server-specific settings for proper bot operation.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Setup system loaded successfully")

    setup = app_commands.Group(
        name='setup', 
        description='Setup commands for server configuration (Staff only)', 
        allowed_installs=discord.app_commands.AppInstallationType(guild=True), 
        allowed_contexts=discord.app_commands.AppCommandContext(guild=True)
    )

    @setup.command(name="roles", description="Set up the roles for the guild (Staff only)")
    @app_commands.describe(type="Select the type of role that you want to assign in the database")
    @app_commands.choices(
        type=[
            app_commands.Choice(name="Bump Role", value="bump"),
            app_commands.Choice(name="Barrel Role", value="mute")
        ]
    )
    async def roles(self, interaction: discord.Interaction, type: str, role: discord.Role):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to set role type=%s", interaction.user.id, interaction.guild.id, type)
        try:
            guild_id = interaction.guild.id
            if type == "bump":
                self.bot.db.set_bump_role(guild_id, role.id)
                await interaction.response.send_message(f"Successfully set {role.mention} as the bump role! Members with this role will be reminded to bump the server daily at 12:00 PM.", ephemeral=True)
            elif type == "mute":
                self.bot.db.set_mute_role(guild_id, role.id)
                await interaction.response.send_message(f"Successfully set {role.mention} as the mute role! Members with this role will not be able to talk in vc.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Failed to set role")
        except Exception as e:
            self.logger.exception("Error occurred while setting role type=%s in guild_id=%s", type, interaction.guild.id)
            await interaction.response.send_message("An error occurred while setting the role. Please try again later.", ephemeral=True)

    @setup.command(name="channels", description="Set a channel in the config (Staff only)")
    @app_commands.describe(type="Select the channel that you want to set in the database")
    @app_commands.choices(
        type=[
            app_commands.Choice(name="Welcome Channel", value="wel"),
            app_commands.Choice(name="Goodbye Channel", value="bye"),
            app_commands.Choice(name="General Channel", value="gen"),
            app_commands.Choice(name="Whisper Channel", value="whi"),
            app_commands.Choice(name="Log Channel", value="log"),
            app_commands.Choice(name="Intro Channel", value="intro"),
            app_commands.Choice(name="Bot Channel", value="bot"),
            app_commands.Choice(name="Color Channel", value="color")
        ]
    )
    async def channels(self, interaction: discord.Interaction, type: str, channel: discord.TextChannel):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to set channel type=%s", interaction.user.id, interaction.guild.id, type)
        try:
            guild = self.bot.db.get_guild(interaction.guild.id)
            guild_id = interaction.guild.id
            channel_id = channel.id
            if type == "wel":
                self.bot.db.set_welcome_channel(guild_id, channel_id)
                await interaction.response.send_message(content=f"Successfully set Welcome Channel to #{channel.name}", ephemeral=True)
            elif type == "bye":
                self.bot.db.set_goodbye_channel(guild_id, channel_id)
                await interaction.response.send_message(content=f"Successfully set Goodbye Channel to #{channel.name}", ephemeral=True)
            elif type == "gen":
                self.bot.db.set_general_channel(guild_id, channel_id)
                await interaction.response.send_message(content=f"Successfully set General Channel to #{channel.name}", ephemeral=True)
            elif type == "whi":
                self.bot.db.set_whisper_channel(guild_id, channel_id)
                await interaction.response.send_message(content=f"Successfully set Whisper Channel to #{channel.name}", ephemeral=True)
            elif type == "log":
                self.bot.db.set_log_channel(guild_id, channel_id)
                await interaction.response.send_message(content=f"Successfully set Log Channel to #{channel.name}", ephemeral=True)
            elif type == "intro":
                self.bot.db.set_intros_channel(guild_id, channel_id)
                await interaction.response.send_message(content=f"Successfully set Intro Channel to #{channel.name}", ephemeral=True)
            elif type == "bot":
                self.bot.db.set_bot_channel(guild_id, channel_id)
                await interaction.response.send_message(content=f"Successfully set Bot Channel to #{channel.name}", ephemeral=True)
            elif type == "color":
                self.bot.db.set_color_channel(guild_id, channel_id)
                await interaction.response.send_message(content=f"Successfully set Color Channel to #{channel.name}", ephemeral=True)
            else:
                await interaction.response.send_message(content=f"Failed to set channel.", ephemeral=True)
        except Exception as e:
            self.logger.exception("Error occurred while setting channel type=%s in guild_id=%s", type, interaction.guild.id)
            await interaction.response.send_message("An error occurred while setting the channel. Please try again later.", ephemeral=True)

    @setup.command(name="tiers", description="Set the role for a specific tier (Staff only)")
    @app_commands.describe(tier="Which tier to set the role for", role="The role to assign to this tier")
    @app_commands.choices(
        tier=[
            app_commands.Choice(name="Tier 1", value=1),
            app_commands.Choice(name="Tier 2", value=2),
            app_commands.Choice(name="Tier 3", value=3)
        ]
    )
    async def tiers(self, interaction: discord.Interaction, tier: int, role: discord.Role):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to set tier role tier=%s", interaction.user.id, interaction.guild.id, tier)
        try:
            guild_id = interaction.guild.id
            if tier not in [1, 2, 3]:
                await interaction.response.send_message("Invalid tier. Please choose 1, 2, or 3.", ephemeral=True)
                return
            self.bot.db.set_tier_role(guild_id, tier, role.id)
            await interaction.response.send_message(f"Set role {role.mention} for Tier {tier}.", ephemeral=True)
        except Exception as e:
            self.logger.exception("Error occurred while setting tier role tier=%s in guild_id=%s", tier, interaction.guild.id)
            await interaction.response.send_message("An error occurred while setting the tier role. Please try again later.", ephemeral=True)

async def setup(bot):
    """Load the SetupCog into the bot."""
    await bot.add_cog(SetupCog(bot)) 