import random, discord, logging
from discord import app_commands
from discord.ext import commands

class Roulette(commands.Cog):
    """
    Roulette gambling game for The Cavern's casino.
    
    Players bet on red, black, or green colors with different payout rates.
    Includes cooldown periods and win/loss tracking.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Roulette game loaded successfully")

    @app_commands.command(name="roulette", description="Play the roulette game")
    @app_commands.describe(bet="The amount of gold you want to bet (Max: 100)", colour="The color you want to bet on")
    @app_commands.choices(colour=[
        app_commands.Choice(name="Red", value="red"),
        app_commands.Choice(name="Black", value="black"),
        app_commands.Choice(name="Green", value="green")
    ])
    @app_commands.checks.cooldown(3, 180)
    async def roulette(self, interaction: discord.Interaction, bet: int, colour: str):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s, bet=%s, colour=%s", interaction.user.id, interaction.guild.id, bet, colour)
        try:
            # Get the user and guild IDs
            user_id = interaction.user.id
            guild_id = interaction.guild.id

            # Get the user's gold
            gold = self.bot.db.get_user_gold(guild_id, user_id)
            print(f"[Roulette] Before bet: {gold}")

            # Check if the user has enough gold to bet
            if gold < bet:
                await interaction.response.send_message(f"You don't have enough gold to bet! You have **{gold}** gold.", ephemeral=True)
                return

            # Check if the color is valid
            if colour.lower() not in ["red", "black", "green"]:
                await interaction.response.send_message("Invalid color! The color must be red, black, or green.", ephemeral=True)
                return

            # Check if the bet is valid
            if bet <= 0 or bet >= 100:
                await interaction.response.send_message("Invalid bet! The bet must 1-100.", ephemeral=True)
                return

            # Set the wheel
            wheel = ["00"] + [str(i) for i in range(0, 37)]
            result = random.choice(wheel)
            result_colour = "green" if result in ["00", "0"] else "red" if int(result) % 2 == 0 else "black"
            result_emoji = "🟢" if result in ["00", "0"] else "🔴" if int(result) % 2 == 0 else "⚫"

            win = colour.lower() == result_colour

            # Add the bet to the user's roulette wins or losses
            if win:
                # Add a roulette win to the user
                self.bot.db.add_roulette_wins(guild_id, user_id)

                payout = bet * 15 if colour.lower() == "green" else bet
                self.bot.db.add_gold(guild_id, user_id, payout)

                # Create an embed to send to the user
                embed = discord.Embed(
                    title="🎡 Roulette", 
                    description=f"The ball landed on **{result}**{result_emoji}.", 
                    color=discord.Color.green()
                    )
                embed.add_field(name="Payout", value=f"You have won **{payout}** gold!", inline=False)

            else:
                # Add a roulette loss to the user
                self.bot.db.add_roulette_losses(guild_id, user_id)

                # Remove the bet from the user's gold
                self.bot.db.remove_gold(guild_id, user_id, bet)

                # Create an embed to send to the user
                embed = discord.Embed(
                    title="🎡 Roulette", 
                    description=f"The ball landed on **{result}**{result_emoji}.", 
                    color=discord.Color.red()
                    )
                embed.add_field(name="Loser!", value=f"You have lost **{bet}** gold!", inline=False)

            # Send a message to the user
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            self.logger.exception("Error occurred while processing roulette command for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while playing roulette. Please try again later.", ephemeral=True)

    @roulette.error
    async def roulette_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            retry_after = round(error.retry_after)
            await interaction.response.send_message(
                f"You're playing too many games! Come back to the roulette wheel in a few minutes",
                ephemeral=True
            )
        else:
            self.logger.exception("Unknown error for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message(
                f"An unknown error occurred. Please try again later. Contact the barkeep if you keep getting this error.",
                ephemeral=True
            )

async def setup(bot):
    """Load the Roulette cog into the bot."""
    await bot.add_cog(Roulette(bot))