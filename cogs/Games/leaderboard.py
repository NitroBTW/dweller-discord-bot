import discord
from discord import app_commands
from discord.ext import commands
import logging

class Leaderboard(commands.Cog):
    """
    Leaderboard system for The Cavern's economy and games.
    
    Displays rankings for gold wealth, gaming statistics, and win rates
    across different categories like blackjack, roulette, and slots.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Leaderboard system loaded successfully")

    @app_commands.command(name="leaderboard", description="Check the leaderboards for a given category")
    @app_commands.describe(category="Which leaderboard would you like to see?")
    @app_commands.choices(
        category=[
            app_commands.Choice(name="Gold", value="gold"),
            app_commands.Choice(name="Blackjack", value="blackjack"),
            app_commands.Choice(name="Roulette", value="roulette"),
            app_commands.Choice(name="Slots", value="slots"),
        ]
    )
    async def leaderboard(self, interaction: discord.Interaction, category: str):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s, category=%s", interaction.user.id, interaction.guild.id, category)
        try:
            # Get the user and guild IDs
            user_id = interaction.user.id
            guild_id = interaction.guild.id

            # Get guild data
            guild_data = self.bot.db.get_guild(guild_id)

            # Check the category
            if category == "gold":
                # Get the user's gold
                user_gold = self.bot.db.get_user_gold(guild_id, user_id)
                # Set the user's place on the leaderboard
                user_place = 0

                # Count users in order of their gold
                sorted_users = sorted(
                    guild_data["users"].items(),
                    key=lambda x: x[1]["gold"],
                    reverse=True
                )

                # Find user's place in the full leaderboard
                for rank, (uid, _) in enumerate(sorted_users, start=1):
                    if int(uid) == user_id:
                        user_place = rank
                        break

                # Define a list for the leaderboard lines
                leaderboard_lines = []

                # Go through only the top 10 users
                for rank, (uid, udata) in enumerate(sorted_users[:10], start=1):
                    # Convert user id into an int
                    uid = int(uid)
                    # Get the user
                    user = self.bot.get_user(uid)
                    # Get the user's username
                    username = user.mention
                    # Get the user's gold
                    gold = udata["gold"]
                    # Add the user to the leaderboard lines
                    leaderboard_lines.append(f"**#{rank}** {username}: **{gold}** gold")

                # Create an embed to send to the user
                embed = discord.Embed(
                    title="Gold Leaderboard", 
                    description="\n".join(leaderboard_lines) or "No users yet.", 
                    color=discord.Color.purple()
                )
                embed.set_footer(text=f"You are #{user_place} in the leaderboard with {user_gold} gold.")

                # Send a message to the user
                await interaction.response.send_message(embed=embed)
            
            elif category == "blackjack":
                # Get the user's blackjack
                user_wins = self.bot.db.get_blackjack_wins(guild_id, user_id)
                # Set the user's place on the leaderboard
                user_place = 0

                # Count users in order of their blackjack wins
                sorted_users = sorted(
                    guild_data["users"].items(),
                    key=lambda x: x[1]["blackjack_wins"],
                    reverse=True
                )

                # Find user's place in the full leaderboard
                for rank, (uid, _) in enumerate(sorted_users, start=1):
                    if int(uid) == user_id:
                        user_place = rank
                        break

                # Define a list for the leaderboard lines
                leaderboard_lines = []

                # Go through only the top 10 users
                for rank, (uid, udata) in enumerate(sorted_users[:10], start=1):
                    # Convert user id into an int
                    uid = int(uid)
                    # Get the user
                    user = self.bot.get_user(uid)
                    # Get the user's username
                    username = user.mention
                    # Get the user's wins
                    wins = udata["blackjack_wins"]
                    # Add the user to the leaderboard lines
                    leaderboard_lines.append(f"**#{rank}** {username}: **{wins}** wins")

                # Create an embed to send to the user
                embed = discord.Embed(
                    title="Blackjack Leaderboard", 
                    description="\n".join(leaderboard_lines) or "No users yet.", 
                    color=discord.Color.purple()
                )
                embed.set_footer(text=f"You are #{user_place} in the leaderboard with {user_wins} wins.")

                # Send a message to the user
                await interaction.response.send_message(embed=embed)

            elif category == "roulette":
                # Get the user's roulette
                user_wins = self.bot.db.get_roulette_wins(guild_id, user_id)
                # Set the user's place on the leaderboard
                user_place = 0

                # Count users in order of their roulette wins
                sorted_users = sorted(
                    guild_data["users"].items(),
                    key=lambda x: x[1]["roulette_wins"],
                    reverse=True
                )

                # Find user's place in the full leaderboard
                for rank, (uid, _) in enumerate(sorted_users, start=1):
                    if int(uid) == user_id:
                        user_place = rank
                        break

                # Define a list for the leaderboard lines
                leaderboard_lines = []

                # Go through only the top 10 users
                for rank, (uid, udata) in enumerate(sorted_users[:10], start=1):
                    # Convert user id into an int
                    uid = int(uid)
                    # Get the user
                    user = self.bot.get_user(uid)
                    # Get the user's username
                    username = user.mention
                    # Get the user's wins
                    wins = udata["roulette_wins"]
                    # Add the user to the leaderboard lines
                    leaderboard_lines.append(f"**#{rank}** {username}: **{wins}** wins")

                # Create an embed to send to the user
                embed = discord.Embed(
                    title="Roulette Leaderboard", 
                    description="\n".join(leaderboard_lines) or "No users yet.", 
                    color=discord.Color.purple()
                )
                embed.set_footer(text=f"You are #{user_place} in the leaderboard with {user_wins} wins.")

                # Send a message to the user
                await interaction.response.send_message(embed=embed)

            elif category == "slots":
                # Get the user's slots
                user_wins = self.bot.db.get_slots_wins(guild_id, user_id)
                # Set the user's place on the leaderboard
                user_place = 0

                # Count users in order of their slots wins
                sorted_users = sorted(
                    guild_data["users"].items(),
                    key=lambda x: x[1]["slots_wins"],
                    reverse=True
                )

                # Find user's place in the full leaderboard
                for rank, (uid, _) in enumerate(sorted_users, start=1):
                    if int(uid) == user_id:
                        user_place = rank
                        break

                # Define a list for the leaderboard lines
                leaderboard_lines = []

                # Go through only the top 10 users
                for rank, (uid, udata) in enumerate(sorted_users[:10], start=1):
                    # Convert user id into an int
                    uid = int(uid)
                    # Get the user
                    user = self.bot.get_user(uid)
                    # Get the user's username
                    username = user.mention
                    # Get the user's wins
                    wins = udata["slots_wins"]
                    # Add the user to the leaderboard lines
                    leaderboard_lines.append(f"**#{rank}** {username}: **{wins}** wins")

                # Create an embed to send to the user
                embed = discord.Embed(
                    title="Slots Leaderboard", 
                    description="\n".join(leaderboard_lines) or "No users yet.", 
                    color=discord.Color.purple()
                )
                embed.set_footer(text=f"You are #{user_place} in the leaderboard with {user_wins} wins.")

                # Send a message to the user
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            self.logger.exception("Error occurred while processing leaderboard command for user_id=%s in guild_id=%s, category=%s", interaction.user.id, interaction.guild.id, category)
            await interaction.response.send_message("An error occurred while fetching the leaderboard. Please try again later.", ephemeral=True)

async def setup(bot):
    """Load the Leaderboard cog into the bot."""
    await bot.add_cog(Leaderboard(bot))