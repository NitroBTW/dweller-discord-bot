import discord
from discord import app_commands
from discord.ext import commands
import logging

class Colour(commands.Cog):
    """
    Colour role management system for The Cavern.
    
    Allows users to select from configured colour roles to customize their
    name appearance. Includes admin tools for managing available colours.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Colour role system loaded successfully")

    colourrole = app_commands.Group(
        name='colorrole', 
        description='Manage color roles (Admin only)', 
        allowed_installs=discord.app_commands.AppInstallationType(guild=True), 
        allowed_contexts=discord.app_commands.AppCommandContext(guild=True)
    )

    colour = app_commands.Group(
        name='color',
        description='Manage your color role',
        allowed_installs=discord.app_commands.AppInstallationType(guild=True), 
        allowed_contexts=discord.app_commands.AppCommandContext(guild=True)
    )

    @colourrole.command(name="add", description="Add a color role to the guild's color list")
    async def add_colour(self, interaction: discord.Interaction, role: discord.Role):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            # Get the guild id
            guild_id = interaction.guild.id
            
            # Check if role is already a colour role
            if self.bot.db.is_colour_role(guild_id, role.id):
                await interaction.response.send_message(f"{role.mention} is already a colour role!", ephemeral=True)
                return
            
            # Add the role to the database
            self.bot.db.add_colour_role(guild_id, role.id, role.name)
            
            await interaction.response.send_message(f"Successfully added {role.mention} as a colour role!", ephemeral=True)
        except Exception as e:
            self.logger.exception("Error occurred for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while adding a color role. Please try again later.", ephemeral=True)

    @colourrole.command(name="remove", description="Remove a color role from the guild's color list")
    async def remove_colour(self, interaction: discord.Interaction, role: discord.Role):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            # Get the guild id
            guild_id = interaction.guild.id
            
            # Check if role is a colour role
            if not self.bot.db.is_colour_role(guild_id, role.id):
                await interaction.response.send_message(f"{role.mention} is not a color role!", ephemeral=True)
                return
            
            # Remove the role from the database
            self.bot.db.remove_colour_role(guild_id, role.id)
            
            await interaction.response.send_message(f"Successfully removed {role.mention} from color roles!", ephemeral=True)
        except Exception as e:
            self.logger.exception("Error occurred for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while removing a color role. Please try again later.", ephemeral=True)

    async def colour_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            # Get the guild id and its colour roles
            guild_id = interaction.guild.id
            colour_roles = self.bot.db.get_colour_roles(guild_id)
            
            # Set the choices to the colours in the guild
            choices = []
            for role_id, role_name in colour_roles.items():
                role = interaction.guild.get_role(int(role_id))
                if role and current.lower() in role_name.lower():
                    choices.append(app_commands.Choice(name=role_name, value=role_id))
            
            return choices[:25]
        except Exception as e:
            self.logger.exception("Error occurred for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            return []

    @colour.command(name="list", description="List all available color roles")
    async def list_colours(self, interaction: discord.Interaction):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            # Get the guild id and its colour roles
            guild_id = interaction.guild.id
            colour_roles = self.bot.db.get_colour_roles(guild_id)
            
            # Check that roles have been setup
            if not colour_roles:
                await interaction.response.send_message("No color roles have been set up yet!", ephemeral=True)
                return
            
            # Create the description with a list of roles
            description = ""
            for role_id, role_name in colour_roles.items():
                role = interaction.guild.get_role(int(role_id))
                if role:
                    description += f"{role_name} - {role.mention}\n"
                else:
                    description += f"(Role not found)\n"
            
            # Set the embed to be sent
            embed = discord.Embed(
                title="Available Color Roles:",
                description=description,
                color=discord.Color.random()
            )
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            self.logger.exception("Error occurred for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while listing color roles. Please try again later.", ephemeral=True)

    @colour.command(name="set", description="Get a color role")
    @app_commands.autocomplete(colour=colour_autocomplete)
    async def set_colour(self, interaction: discord.Interaction, colour: str):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            # Get the id of the guild and user
            guild_id = interaction.guild.id
            user = interaction.user
            
            # Check if the colour role exists
            if not self.bot.db.is_colour_role(guild_id, int(colour)):
                await interaction.response.send_message("That color role doesn't exist!", ephemeral=True)
                return
            
            # Get the role from the id
            role = interaction.guild.get_role(int(colour))

            # Check that the role exists
            if not role:
                await interaction.response.send_message("That role no longer exists!", ephemeral=True)
                return
            
            # Get the list of colour roles from the db
            colour_roles = self.bot.db.get_colour_roles(guild_id)

            # Go through the user's roles and remove them if they match a colour from the db
            for role_id in colour_roles.keys():
                existing_role = interaction.guild.get_role(int(role_id))
                if existing_role and existing_role in user.roles:
                    await user.remove_roles(existing_role)
            
            # Add the new colour role
            await user.add_roles(role)
            
            await interaction.response.send_message(f"You now have the {role.mention} color!", ephemeral=True)
        except Exception as e:
            self.logger.exception("Error occurred for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while setting your color role. Please try again later.", ephemeral=True)

    @colour.command(name="clear", description="Remove your current color role")
    async def clear_colour(self, interaction: discord.Interaction):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            guild_id = interaction.guild.id
            member = interaction.user
            
            # Remove all colour roles from the user
            colour_roles = self.bot.db.get_colour_roles(guild_id)
            removed_roles = []
            
            for role_id in colour_roles.keys():
                role = interaction.guild.get_role(int(role_id))
                if role and role in member.roles:
                    await member.remove_roles(role)
                    removed_roles.append(role.name)
            
            if removed_roles:
                await interaction.response.send_message(f"Removed color roles: {', '.join(removed_roles)}", ephemeral=True)
            else:
                await interaction.response.send_message("You don't have any color roles to remove!", ephemeral=True)
        except Exception as e:
            self.logger.exception("(Colour.clear_colour) Error occurred for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while clearing your color roles. Please try again later.", ephemeral=True)

async def setup(bot):
    """Load the Colour cog into the bot."""
    await bot.add_cog(Colour(bot))
