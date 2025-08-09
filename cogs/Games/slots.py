import time
import discord, random
from discord import app_commands, Button
from discord.ext import commands
import asyncio
import logging



class SlotsView(discord.ui.View):
    def __init__(self, bot, user_id: int, guild_id: int, bet: int):
        # Declare the variables
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.bet = bet
        super().__init__()
    
    async def interaction_check(self, interaction):
        return interaction.user.id == int(self.user_id)
    
    @discord.ui.button(label="Spin", style=discord.ButtonStyle.blurple)
    async def spin(self, interaction: discord.Interaction, button: Button):
        # Define the slot emojis
        emojis = ["🍒", "🍋", "🍊", "🍇", "🍉", "7️⃣"]
        weights = [0.265, 0.25, 0.22, 0.18, 0.08, 0.005]

        # Write the embed for the start of the spin
        embed = discord.Embed(
            title="🎰 Slot Machine",
            color=discord.Color.gold()
        )
        embed.add_field(name="Spinning the machine...", value="`?` `?` `?`", inline=False)

        # Send the initial spinning message
        await interaction.response.edit_message(embed=embed, view=None)

        # Set a list for results
        results = ["?", "?", "?"]
        message = await interaction.original_response()

        # Loop through the 3 lanes
        for i in range(3):
            # 1 second per lane
            await asyncio.sleep(1)
            # Get the random result for this lane
            result = random.choices(emojis, weights=weights)[0]
            # Set the result into the list
            results[i] = result
            # Set the value for the embed field
            value = " ".join(f"`{j}`" for j in results)
            # Set the embed for editing
            embed = discord.Embed(
                title="🎰 Slot Machine",
                color=discord.Color.gold()
            )
            embed.add_field(name="Spinning the machine...", value=value, inline=False)
            # Send the embed
            await message.edit(embed=embed)

        # Set a,b,c to results
        a, b, c = results
        
        # All lanes are matching 7s
        if a == b == c == "7️⃣":
            # Set the payout amount
            payout = self.bet * 49
            # Add the payout to the user's database
            self.bot.db.add_gold(self.guild_id, self.user_id, payout)
            # Set the embed for editing
            embed = discord.Embed(
                title="🎰 Slot Machine",
                color=discord.Color.gold()
            )
            embed.add_field(name="Mega Jackpot!", value=f"`{a}` `{b}` `{c}`", inline=False)
            embed.add_field(name="Payout", value=f"You won **{payout}** gold!", inline=False)
            # Send the embed
            await message.edit(embed=embed, view=None)

        # All lanes are matching melons
        if a == b == c == "🍉":
            # Set the payout amount
            payout = self.bet * 9
            # Add the payout to the user's database
            self.bot.db.add_gold(self.guild_id, self.user_id, payout)
            # Set the embed for editing
            embed = discord.Embed(
                title="🎰 Slot Machine",
                color=discord.Color.gold()
            )
            embed.add_field(name="Big Jackpot!", value=f"`{a}` `{b}` `{c}`", inline=False)
            embed.add_field(name="Payout", value=f"You won **{payout}** gold!", inline=False)
            # Send the embed
            await message.edit(embed=embed, view=None)
        
        # All lanes are matching, not 7s or melons
        elif a == b == c:
            # Set the payout amount
            payout = self.bet * 7
            # Add the payout to the user's database
            self.bot.db.add_gold(self.guild_id, self.user_id, payout)
            # Set the embed for editing
            embed = discord.Embed(
                title="🎰 Slot Machine",
                color=discord.Color.gold()
            )
            embed.add_field(name="Jackpot!", value=f"`{a}` `{b}` `{c}`", inline=False)
            embed.add_field(name="Payout", value=f"You won **{payout}** gold!", inline=False)
            # Send the embed
            await message.edit(embed=embed, view=None)

        # Two lanes are matching
        elif (a == b) or (b == c) or (c == a):
            # Set the payout amount
            payout = self.bet * 2
            # Add the payout to the user's database
            self.bot.db.add_gold(self.guild_id, self.user_id, payout)
            # Set the embed for editing
            embed = discord.Embed(
                title="🎰 Slot Machine",
                color=discord.Color.gold()
            )
            embed.add_field(name="Two of a kind!", value=f"`{a}` `{b}` `{c}`", inline=False)
            embed.add_field(name="Payout", value=f"You won **{payout}** gold!", inline=False)
            # Send the embed
            await message.edit(embed=embed, view=None)

        # They lost the slot machine
        else:
            # Remove the gold from the user in the database
            self.bot.db.remove_gold(self.guild_id, self.user_id, self.bet)
            # Set the embed for editing
            embed = discord.Embed(
                title="🎰 Slot Machine",
                color=discord.Color.gold()
            )
            embed.add_field(name="No win this time, Try again!", value=f"`{a}` `{b}` `{c}`", inline=False)
            embed.add_field(name="Payout", value=f"You lost **{self.bet}** gold!", inline=False)
            # Send the embed
            await message.edit(embed=embed, view=None)

    # Disable the buttons on discord's response timeout
    async def on_timeout(self):
        self.disable_all()
    
    def disable_all(self):
        for item in self.children:
            item.disabled = True



class Slots(commands.Cog):
    """
    Slot machine game for The Cavern's casino.
    
    Interactive slot machine with spin animation, multiple win conditions,
    and varying payout rates based on symbol combinations.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Slots game loaded successfully")

    @app_commands.command(name="slots", description="Try your luck on the slot machine!")
    @app_commands.describe(bet="The amount of gold you want to bet (Max 100)")
    @app_commands.checks.cooldown(3, 180)
    async def slots(self, interaction: discord.Interaction, bet: int):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s, bet=%s", interaction.user.id, interaction.guild.id, bet)
        try:
            # Get the user and guild IDs
            user_id = interaction.user.id
            guild_id = interaction.guild.id

            # Get the user's gold
            gold = self.bot.db.get_user_gold(guild_id, user_id)

            # Check if the user has enough gold to bet
            if gold < bet:
                await interaction.response.send_message(f"You don't have enough gold to bet! You have **{gold}** gold.", ephemeral=True)
                return

            # Check if the bet is valid
            if bet <= 0:
                await interaction.response.send_message("Invalid bet! The bet must be greater than 0.", ephemeral=True)
                return

            # Create an embed to send to the user
            embed = discord.Embed(
                title="🎰 Slot Machine", 
                color=discord.Color.gold()
                )
            embed.add_field(name="Spin to win!", value="Hit the button below to spin the machine!")

            # Define the view for the response
            view = SlotsView(
                bot = self.bot,
                user_id=user_id,
                guild_id=guild_id,
                bet=bet
            )
            
            # Send the response and activate the game
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            self.logger.exception("Error occurred while processing slots command for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while playing slots. Please try again later.", ephemeral=True)

    @slots.error
    async def slots_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            retry_after = round(error.retry_after)
            await interaction.response.send_message(
                f"You're playing too many games! Come back to the slot machine in a few minutes",
                ephemeral=True
            )
        else:
            self.logger.exception("Unknown error for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message(
                f"An unknown error occurred. Please try again later. Contact the barkeep if you keep getting this error.",
                ephemeral=True
            )

async def setup(bot):
    """Load the Slots cog into the bot."""
    await bot.add_cog(Slots(bot))