import discord
from discord import app_commands
from discord.ext import commands
import logging

class Help(commands.Cog):
    """
    Help system for The Cavern Discord bot.
    
    Provides interactive help menus, shop information, and game overviews.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Help cog loaded successfully")

    @app_commands.command(name="help", description="A little guide to the server and the dweller")
    async def help_menu(self, interaction: discord.Interaction):
        """
        Display the main help menu with server guide and command reference.
        
        Shows a comprehensive guide to The Cavern with dynamic channel mentions
        and all available bot features organized in themed sections.
        """
        self.logger.info("Help menu requested by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            guild_id = interaction.guild.id
            
            # Get configured channel IDs for dynamic mentions
            intros_channel_id = self.bot.db.get_intros_channel(guild_id)
            color_channel_id = self.bot.db.get_color_channel(guild_id)
            
            # Create channel mentions or fallback to generic names
            intros_mention = f'<#{intros_channel_id}>' if intros_channel_id else '#intros'
            color_mention = f'<#{color_channel_id}>' if color_channel_id else '#colors'

            # Build the main help embed with themed content
            embed = discord.Embed(
                title="Welcome to The Cavern!",
                description="Here's a quick guide to help you get started and make the most of the server and bot features.",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="Getting Started",
                value=f"Introduce yourself in {intros_mention} and meet the community!",
                inline=False
            )
            embed.add_field(
                name="Decorate Your Profile",
                value=f"Personalize your name color using the `/color` command in {color_mention}.",
                inline=False
            )
            embed.add_field(
                name="Grow Your Wealth",
                value="Earn gold by chatting and claiming your daily reward with `/daily`. Spend it in the `/shop` or try your luck with `/games`!",
                inline=False
            )
            embed.add_field(
                name="Games",
                value="Play `/blackjack`, `/roulette`, or `/slots` to win (or lose) gold!",
                inline=False
            )
            embed.add_field(
                name="Shop",
                value="Use `/shop` to see what you can buy, like Mimic's Curse or Barrel Time.",
                inline=False
            )
            embed.add_field(
                name="Useful Commands",
                value=(
                    "`/balance` — Check your gold\n"
                    "`/daily` — Claim your daily gold\n"
                    "`/leaderboard` — See the richest members\n"
                    "`/color` — Set or clear your name color\n"
                    "`/shop` — View the shop\n"
                    "`/buy` — Purchase shop items\n"
                    "`/games` — See available games\n"
                    "`/help` — Show this menu"
                ),
                inline=False
            )
            embed.set_footer(text="If you have any questions, ask a bartender for help!")
            
            # Send the help menu to the user
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            self.logger.exception("Error occurred while showing help menu for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while showing the help menu. Please try again later.", ephemeral=True)

    @app_commands.command(name="shop", description="View the shop menu")
    async def shop_menu(self, interaction: discord.Interaction):
        """
        Display the shop menu with available items and prices.
        
        Shows The Cavern's shop with themed items like Mimic's Curse and
        Barrel Time, including pricing and descriptions.
        """
        self.logger.info("Shop menu requested by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            # Create themed shop embed
            embed = discord.Embed(title="The Menu", color=discord.Color.gold())
            
            # Mimic's Curse item details
            embed.add_field(
                name="Mimic's curse", 
                value="Pay the Dweller to cast a Mimic's Curse upon a user and temporarily change their nickname for up to 12 hours.", 
                inline=True
            )
            embed.add_field(
                name="Prices", 
                value="1h - **1500** gold\n6h - **6000** gold\n12h  - **10000** gold", 
                inline=True
            )
            embed.add_field(name=" ", value="", inline=False)  # Spacer
            
            # Future item placeholder
            embed.add_field(name="Trigger", value="(Coming Soon)", inline=True)
            embed.add_field(name="Prices", value="(Coming Soon)", inline=True)
            embed.add_field(name=" ", value="", inline=False)  # Spacer
            
            # Barrel Time item details
            embed.add_field(
                name="Barrel Time", 
                value="Pay the Dweller to throw the pesky drunked in a beer keg (Mutes and deletes their messages for 5 minutes)", 
                inline=True
            )
            embed.add_field(name="Price", value="5m - **800** gold", inline=True)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            self.logger.exception("Error occurred while showing shop menu for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while showing the shop menu. Please try again later.", ephemeral=True)

    @app_commands.command(name="games", description="See what games we have")
    async def game_menu(self, interaction: discord.Interaction):
        """
        Display the available casino games with descriptions.
        
        Shows all gambling games available in The Cavern's casino.
        """
        self.logger.info("Game menu requested by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
        try:
            # Create the games library embed
            embed = discord.Embed(title="Game Library", color=discord.Color.gold())
            embed.add_field(
                name="Blackjack", 
                value="Play a game of Blackjack against the dealer", 
                inline=False
            )
            embed.add_field(
                name="Roulette", 
                value="Try your luck on the roulette wheel", 
                inline=False
            )
            embed.add_field(
                name="Slots", 
                value="Try your luck on the slot machine", 
                inline=False
            )
            embed.set_footer(text="The tinkerer swears he made all games fair.")
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            self.logger.exception("Error occurred while showing game menu for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while showing the game menu. Please try again later.", ephemeral=True)

    

async def setup(bot):
    """Load the Help cog into the bot."""
    await bot.add_cog(Help(bot))