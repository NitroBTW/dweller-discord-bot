from discord.ui import Button, View
import discord, operator
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from random import shuffle, choice
import logging

# Get the value of a hand
def hand_value(hand):
    # Total value
    value = 0
    # Value for aces
    aces = 0
    for card in hand:
        # Face cards
        if card.value in [11,12,13]:
            value += 10
        
        # Count how many aces there are and count them as 11 for now
        elif card.value == 1:
            value += 11
            aces += 1
        
        else:
            value += int(card.value)
        
    # If the value is more than 21 but there are aces, set them to 1 until the value is less than or equal to 21
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# Format the hand to "x(symbol), y(symbol)"
def format_hand(hand):
    return "  ".join(f"`{card.name}`" for card in hand)


class BlackjackView(discord.ui.View):
    def __init__(self, bot, user_id: int, guild_id: int, bet: int, player_hand, dealer_hand, deck):
        # Declare the variables
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.bet = bet
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.deck = deck
        self.stopped = False
        super().__init__()
        
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: Button):
        if self.stopped:
            return
        
        # Add a card to the player's hand and add the value to their total
        self.player_hand.append(self.deck.give_random_card())
        player_val = hand_value(self.player_hand)

        # If the player is bust
        if player_val > 21:
            # Stop the game and disable the buttons
            self.stopped = True
            self.disable_all()

            # Remove the player's bet and add a loss
            self.bot.db.remove_gold(self.guild_id, self.user_id, self.bet)
            self.bot.db.add_blackjack_losses(self.guild_id, self.user_id)

            # End the game as a loss
            await self.end_game(
                interaction=interaction, 
                result="Bust! You lose.", 
                multiplier=0
                )

        else:
            # Format the player's hand and get the dealer's revealed card
            formatted_hand = format_hand(self.player_hand)
            dealer_shows = self.dealer_hand[0].name

            # Create the embed to edit the original response
            embed = discord.Embed(
                title="🃏 Blackjack",
                color=discord.Color.orange()
            )
            # Add the player's hand and dealer's shown card as a field
            embed.add_field(name="Your Hand", value=f"{formatted_hand} ({player_val})", inline=False)
            embed.add_field(name="Dealer Shows", value=f"`{dealer_shows}`", inline=False)
            embed.add_field(name="Bet", value=f"**{self.bet}** gold")
            
            # Edit the original response to the command
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.blurple)
    async def stand(self, interaction: discord.Interaction, button: Button):
        if self.stopped:
            return
        
        self.stopped = True
        self.disable_all()

        # Force the dealer to hit below 17
        while hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.give_random_card())
        
        # Get the value of the player and dealer hands
        player_val = hand_value(self.player_hand)
        dealer_val = hand_value(self.dealer_hand)

        # If the dealer is bust, user wins
        if dealer_val > 21:
            self.bot.db.add_blackjack_wins(self.guild_id, self.user_id)
            await self.end_game(
                interaction=interaction,
                result="Dealer busts! You win!",
                multiplier=1.5
            )
        # If the player is above the dealer and below 21, user wins
        elif player_val > dealer_val:
            self.bot.db.add_blackjack_wins(self.guild_id, self.user_id)
            await self.end_game(
                interaction=interaction,
                result="You win!",
                multiplier=1.5
            )
        # If the player is below the dealer and both below 21, dealer wins
        elif dealer_val > player_val:
            self.bot.db.add_blackjack_losses(self.guild_id, self.user_id)
            await self.end_game(
                interaction=interaction,
                result="You lose!",
                multiplier=0
            )
        # If the player is below the dealer and both below 21, dealer wins
        else:
            self.bot.db.add_blackjack_losses(self.guild_id, self.user_id)
            await self.end_game(
                interaction=interaction,
                result="It's a draw!",
                multiplier=1
            )
        
    async def end_game(self, interaction: discord.Interaction, result: str, multiplier: int):
        # Get the value of the player and dealer hands
        player_val = hand_value(self.player_hand)
        dealer_val = hand_value(self.dealer_hand)

        # Payout
        payout = round(self.bet * multiplier)
        if multiplier > 1:
            payout_text = f"You won **{payout}** gold!"
            self.bot.db.add_gold(self.guild_id, self.user_id, payout)
        elif multiplier == 1:
            payout_text = f"You gain nothing"
        else:
            payout_text = f"You lost **{self.bet}** gold"

        # Get the user's wins and losses
        user_winloss = self.bot.db.get_blackjack_winloss(self.guild_id, self.user_id)

        # Format the player/dealer hands
        player_hand_formatted = format_hand(self.player_hand)
        dealer_hand_formatted = format_hand(self.dealer_hand)

        embed = discord.Embed(
            title=f"🃏 Blackjack - {result}",
            color=discord.Color.green() if multiplier > 1 else discord.Color.orange() if multiplier == 1 else discord.Color.red()
            )
        embed.add_field(name="Your Hand", value=f"{player_hand_formatted} ({player_val})", inline=False)
        embed.add_field(name="Dealer Hand", value=f"{dealer_hand_formatted} ({dealer_val})", inline=False)
        
        embed.add_field(name="Payout", value=f"{payout_text}")
        embed.set_footer(text=f"W/L: {user_winloss[0]}/{user_winloss[1]}   Winrate: {user_winloss[2]}%")

        await interaction.response.edit_message(embed=embed, view=None)
    
    async def on_timeout(self):
        self.disable_all()
    
    def disable_all(self):
        for item in self.children:
            item.disabled = True


class Blackjack(commands.Cog):
    """
    Interactive Blackjack game for The Cavern's casino.
    
    Full-featured card game with hit/stand buttons, dealer AI,
    and comprehensive win/loss tracking. Supports betting with gold.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Blackjack game loaded successfully")

    @app_commands.command(name="blackjack", description="Play a game of blackjack!")
    @app_commands.describe(bet="The amount of gold you want to bet (Max: 100)")
    @app_commands.checks.cooldown(3, 180)
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
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
            if bet <= 0 or bet >= 100:
                await interaction.response.send_message("Invalid bet! The bet must be 1-100 gold.", ephemeral=True)
                return
            
            # Create the deck of cards for the game and shuffle it
            deck = DeckOfCards()
            deck.shuffle_deck()

            # Create the player's and dealer's hand
            player_hand = [deck.give_random_card(), deck.give_random_card()]
            dealer_hand = [deck.give_random_card(), deck.give_random_card()]

            # Format the hands
            player_hand_formatted = format_hand(player_hand)
            dealer_hand_formatted = format_hand(dealer_hand)

            # Get the player's and dealer's hands' value
            player_val = hand_value(player_hand)
            dealer_val = hand_value(dealer_hand)

            # Check if the player has already bust
            if player_val > 21:
                # Remove the player's bet and add a loss
                self.bot.db.remove_gold(guild_id, user_id, bet)
                self.bot.db.add_blackjack_losses(guild_id, user_id)

                # Get the user's wins and losses
                user_wins = self.bot.db.get_blackjack_wins(guild_id, user_id)
                user_losses = self.bot.db.get_blackjack_losses(guild_id, user_id)
                user_games = user_wins + user_losses
                user_winrate = round((user_wins / (user_games) * 100), 1) if user_games > 0 else 0

                # Create the embed for the response
                embed = discord.Embed(
                    title="🃏 Blackjack - Bust!",
                    color=discord.Color.red()
                )
                embed.add_field(name="Your Hand", value=f"{player_hand_formatted} ({player_val})", inline=False)
                embed.add_field(name="Dealer Hand", value=f"{dealer_hand_formatted} ({dealer_val})", inline=False)
                embed.add_field(name="Payout", value=f"You lost **{bet}** gold", inline=False)
                embed.set_footer(text=f"W/L: {user_wins}/{user_losses}   Winrate: {user_winrate}%")

                # Send the embed in response
                await interaction.response.send_message(embed=embed)
                return
            
            # Create the discord view
            view = BlackjackView(
                bot=self.bot,
                user_id=user_id,
                guild_id=guild_id,
                bet=bet,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                deck=deck
            )

            # Create the embed for the game
            embed = discord.Embed(
                title="🃏 Blackjack",
                color=discord.Color.orange()
            )
            embed.add_field(name="Your Hand", value=f"{player_hand_formatted} ({player_val})", inline=False)
            embed.add_field(name="Dealer Shows", value=f"{dealer_hand[0].name}", inline=False)
            embed.add_field(name="Bet", value=f"**{bet}** gold")
            
            # Respond to the command
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            self.logger.exception("Error occurred for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while playing blackjack. Please try again later.", ephemeral=True)
    
    @blackjack.error
    async def blackjack_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            retry_after = round(error.retry_after)
            await interaction.response.send_message(
                f"You're playing too many games! Come back to the blackjack table in a few minutes",
                ephemeral=True
            )
        else:
            self.logger.exception("Unknown error for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message(
                f"An unknown error occurred. Please try again later. Contact the barkeep if you keep getting this error.",
                ephemeral=True
            )


async def setup(bot):
    """Load the Blackjack cog into the bot."""
    await bot.add_cog(Blackjack(bot))



# ~~~~~~~~~~~~~~~~~~~~~~~~~~ Card and Deck classes ~~~~~~~~~~~~~~~~~~~~~~~~~~
class Card(object):
    # Initialise the card object
    def __init__(self, suit_rank_tup):
        self.suit = suit_rank_tup[0]
        self.rank = suit_rank_tup[1]
        self.value = self.rank
        self.name = self._translate_card()
        self.image_path = ""
        self.image_obj = None

    @staticmethod
    def _assign_names(rank):
        if isinstance(rank, int):

            if rank == 1:
                return "A"

            elif rank == 11:
                return "J"

            elif rank == 12:
                return "Q"

            elif rank == 13:
                return "K"
            
            else:
                return str(rank)

    # Get the character and suit of a card
    def _translate_card(self):
        if isinstance(self.suit, int):

            if self.suit == 0:
                self.name = "{} ♠".format(self._assign_names(self.rank))

            elif self.suit == 1:
                self.name = "{} ♥".format(self._assign_names(self.rank))

            elif self.suit == 2:
                self.name = "{} ♦".format(self._assign_names(self.rank))

            elif self.suit == 3:
                self.name = "{} ♣".format(self._assign_names(self.rank))

        return self.name


class DeckOfCards(object):

    # A list of 52 cards as tuples with a suit and rank
    suits_ranks = [
        (
            i % 4,
            13 if i % 13 == 0 else i % 13
        )
        for i in range(1, 53)
    ]

    # Initialises a deck of cards when called
    def __init__(self):
        # Convert the suits_ranks list to card objects
        self.deck = [
            Card(tup)
            for tup in self.suits_ranks
        ]

    # Shuffle the deck
    def shuffle_deck(self):
        shuffle(self.deck)
        return self.deck

    # Get a random card and remove it from the deck
    def give_random_card(self):
        card = choice(self.deck)

        for card_obj in self.deck:
            if card_obj.name == card.name:
                self.deck.remove(card_obj)
        return card
