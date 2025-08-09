import discord, asyncio, math, logging
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta

class Shop(commands.Cog):
    """
    Shopping system for The Cavern's economy.
    
    Provides purchasable items including Mimic's Curse (nickname changes),
    Barrel Time (temporary muting), and future items. Handles gold transactions
    and automatic effect reversions.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Shop system loaded successfully")
        self.revert_task.start()  # Start automatic effect reversion task

    def cog_unload(self):
        self.revert_task.cancel()

    buy = app_commands.Group(name="buy", description="Buy items from the shop")

    @buy.command(name="mimic", description="Temporarily change a user's nickname.")
    @app_commands.describe(user="The user to cast a mimic's curse upon", duration="How long to curse them for")
    @app_commands.choices(duration=[
        app_commands.Choice(name="1 Hour", value="1h"),
        app_commands.Choice(name="6 Hours", value="6h"),
        app_commands.Choice(name="12 Hours", value="12h")
    ])
    async def buy_mimic(self, interaction: discord.Interaction, user: discord.Member, duration: str):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to buy mimic for user_id=%s, duration=%s", interaction.user.id, interaction.guild.id, user.id, duration)
        try:
            # Check if user is trying to mimic themselves
            if user.id == interaction.user.id:
                await interaction.response.send_message("You can't curse yourself!", ephemeral=True)
                return
            
            # Check if user is a bot
            if user.bot:
                await interaction.response.send_message("You can't curse the Dweller!", ephemeral=True)
                return
            
            # Check if user already has a mimic active
            mimic_expiry = self.bot.db.get_mimic_expiry(interaction.guild.id, user.id)
            if mimic_expiry:
                expiry_time = datetime.fromisoformat(mimic_expiry)
                if expiry_time > datetime.utcnow():
                    remaining = (expiry_time - datetime.utcnow()).total_seconds()
                    hours = max(1, math.ceil(remaining / 3600))
                    await interaction.response.send_message(
                        f"That user is already cursed for another {hours} hour{'s' if hours != 1 else ''}.",
                        ephemeral=True
                    )
                    return
            
            # Check gold
            gold = self.bot.db.get_user_gold(interaction.guild.id, interaction.user.id)
            price = mimic_options[duration][0]
            if gold < price:
                await interaction.response.send_message(f"You don't have enough gold! You need {price} gold.", ephemeral=True)
                return
            
            # Show modal
            await interaction.response.send_modal(MimicModal(self.bot, user, duration, interaction.user, log_guild=interaction.guild, log_func=self.send_log_embed))
        except Exception as e:
            self.logger.exception("Error occurred while processing mimic purchase for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while processing the mimic purchase. Please try again later.", ephemeral=True)

    @buy.command(name="trigger", description="(Coming soon)")
    async def buy_trigger(self, interaction: discord.Interaction):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to buy trigger", interaction.user.id, interaction.guild.id)
        try:
            await interaction.response.send_message("Trigger is coming soon!", ephemeral=True)
        except Exception as e:
            self.logger.exception("Error occurred while processing trigger purchase for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while processing the trigger purchase. Please try again later.", ephemeral=True)

    @buy.command(name="barrel_time", description="Send a user to the barrel for 5 minutes (**800** gold)")
    @app_commands.describe(user="The user to send to the barrel")
    async def buy_barrel_time(self, interaction: discord.Interaction, user: discord.User):
        self.logger.info("Command invoked by user_id=%s in guild_id=%s to buy barrel_time for user_id=%s", interaction.user.id, interaction.guild.id, user.id)
        try:
            target = user
            # Get relevant IDs
            guild_id = interaction.guild.id
            user_id = interaction.user.id
            target_id = user.id

            # Check if user is trying to mimic themselves
            if target_id == user_id:
                await interaction.response.send_message("You can't curse yourself!", ephemeral=True)
                return
            
            # Check if the user is trying to curse the dweller
            if target_id == self.bot.user.id:
                await interaction.response.send_message("You cannot curse the Dweller!", ephemeral=True)
                return

            # Check if user is a bot
            elif target.bot:
                await interaction.response.send_message("You can't curse the Dweller!", ephemeral=True)
                return

            # Check if the target is already in the barrel
            barrel_expiry = self.bot.db.get_barrel_expiry(guild_id, target_id)
            if barrel_expiry:
                expiry_time = datetime.fromisoformat(barrel_expiry)
                if expiry_time > datetime.utcnow():
                    remaining = (expiry_time - datetime.utcnow()).total_seconds()
                    minutes = max(1, math.ceil(remaining / 60))
                    await interaction.response.send_message(
                        f"That user is already in the barrel for another {minutes} minute{'s' if minutes != 1 else ''}.",
                        ephemeral=True
                    )
                    return
            
            # Check gold
            gold = self.bot.db.get_user_gold(interaction.guild.id, interaction.user.id)
            price = 800
            if gold < price:
                await interaction.response.send_message(f"You don't have enough gold! You need {price} gold.", ephemeral=True)
                return

            # Set the target to be in the barrel
            expiry = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            self.bot.db.set_barrel_expiry(guild_id, target_id, expiry)
            # Get the role and give it to the user
            barrel_role_id = self.bot.db.get_mute_role(guild_id)
            if barrel_role_id:
                barrel_role = interaction.guild.get_role(int(barrel_role_id))
                if barrel_role:
                    await target.add_roles(barrel_role)
                    try:
                        await target.edit(mute=True)
                    except Exception as e:
                        self.logger.error(f"Failed to mute {target.name} user: {e}")

            await interaction.response.send_message(f"You have put {target.mention} in the barrel!", ephemeral=True)
            # Discord log for barrel purchase
            await self.send_log_embed(
                interaction.guild,
                title="Barrel Time Purchased",
                details=f"{interaction.user.mention} put {target.mention} in the barrel for 5 minutes.",
                color=discord.Color.orange()
            )
        except Exception as e:
            self.logger.exception("Error occurred while processing barrel_time purchase for user_id=%s in guild_id=%s", interaction.user.id, interaction.guild.id)
            await interaction.response.send_message("An error occurred while processing the barrel time purchase. Please try again later.", ephemeral=True)

    @tasks.loop(minutes=1)
    async def revert_task(self):
        self.logger.info("Running revert task for expired mimics and barrels")
        try:
            # Check all guilds and users for expired mimics
            now = datetime.utcnow()
            for guild_id_str, guild_data in self.bot.db.data.items():
                guild_id = int(guild_id_str)
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    continue
                for user_id_str, user_data in guild_data["users"].items():
                    mimic_expiry = user_data.get("mimic_expiry")
                    if mimic_expiry:
                        try:
                            expiry_time = datetime.fromisoformat(mimic_expiry)
                        except Exception:
                            continue
                        if expiry_time <= now:
                            member = guild.get_member(int(user_id_str))
                            if member:
                                try:
                                    await member.edit(nick=None, reason="Mimic expired")
                                except Exception as e:
                                    self.logger.error(f"Failed to revert nickname for {member}: {e}")
                                self.bot.db.set_mimic_expiry(guild_id, int(user_id_str), None)
                                # Discord log for mimic revert
                                await self.send_log_embed(
                                    guild,
                                    title="Mimic Reverted",
                                    details=f"{member.mention}'s mimic curse was reverted successfully.",
                                    color=discord.Color.orange()
                                )

                    barrel_expiry = user_data.get("barrel_expiry")
                    if barrel_expiry:
                        try:
                            expiry_time = datetime.fromisoformat(barrel_expiry)
                        except Exception:
                            continue
                        if expiry_time <= now:
                            member = guild.get_member(int(user_id_str))
                            if member:
                                try:
                                    barrel_role_id = self.bot.db.get_mute_role(guild_id)
                                    if barrel_role_id:
                                        barrel_role = guild.get_role(int(barrel_role_id))
                                        if barrel_role:
                                            await member.remove_roles(barrel_role)
                                            await member.edit(mute=False)
                                except Exception as e:
                                    self.logger.error(f"Failed to revert barrel time for {member}: {e}")
                            self.bot.db.set_barrel_expiry(guild_id, int(user_id_str), None)
                            # Discord log for barrel revert
                            await self.send_log_embed(
                                guild,
                                title="Barrel Time Ended",
                                details=f"{member.mention}'s barrel time has ended and their role was removed.",
                                color=discord.Color.orange()
                            )
        except Exception as e:
            self.logger.exception("Error occurred in revert_task loop")

    @revert_task.before_loop
    async def before_revert(self):
        await self.bot.wait_until_ready()

    async def send_log_embed(self, guild, title, details, color=discord.Color.orange()):
        log_channel_id = self.bot.db.get_log_channel(guild.id)
        if not log_channel_id:
            return
        channel = guild.get_channel(int(log_channel_id))
        if not channel:
            return
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name="Details", value=details, inline=False)
        embed.timestamp = datetime.utcnow()
        await channel.send(embed=embed)

async def setup(bot):
    """Load the Shop cog into the bot."""
    await bot.add_cog(Shop(bot)) 



mimic_options = {
    "1h": (1500,1),
    "6h": (6000,6),
    "12h": (10000,12)
}

class MimicModal(discord.ui.Modal, title="Mimic Nickname"):
    nickname = discord.ui.TextInput(
        label="Enter the new nickname for the target",
        style=discord.TextStyle.short,
        max_length=32,
        required=True
    )

    def __init__(self, bot, target: discord.Member, duration: str, buyer: discord.Member, log_guild=None, log_func=None):
        super().__init__()
        self.bot = bot
        self.target = target
        self.duration = duration
        self.buyer = buyer
        self.log_guild = log_guild
        self.log_func = log_func

    async def on_submit(self, interaction: discord.Interaction):
        # Get the guild, buyer, and user id
        guild_id = interaction.guild.id
        user_id = self.target.id
        buyer_id = self.buyer.id
        # Get the integer prices and hours that the user chose
        price, hours = mimic_options[self.duration]
        # Get the buyer's money to make sure they can afford it
        gold = self.bot.db.get_user_gold(guild_id, buyer_id)

        # Check gold again (in case it changed)
        if gold < price:
            await interaction.response.send_message(f"You don't have enough gold! You need {price} gold.", ephemeral=True)
            return

        # Set nickname
        try:
            await self.target.edit(nick=self.nickname.value, reason=f"Mimic purchased by {self.buyer.display_name}")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to change that user's nickname.", ephemeral=True)
            return
        except Exception as e:
            await interaction.response.send_message(f"Failed to change nickname: {e}", ephemeral=True)
            return
        
        # Deduct gold
        self.bot.db.remove_gold(guild_id, buyer_id, price)

        # Set mimic expiry in DB
        expiry = (datetime.utcnow() + timedelta(hours=hours)).isoformat()
        self.bot.db.set_mimic_expiry(guild_id, user_id, expiry)

        await interaction.response.send_message(f"{self.target.mention}'s nickname has been changed to '{self.nickname.value}' for {self.duration.replace('h', ' hour(s)')}.", ephemeral=True)

        # Announce in general channel
        general_channel_id = self.bot.db.get_general_channel(guild_id)
        if general_channel_id:
            channel = interaction.guild.get_channel(int(general_channel_id))
            if channel:
                embed = discord.Embed(
                    title="Somebody has placed a mimic's curse!",
                    description=f"Enjoy your new name {self.target.mention}",
                    color=discord.Color.purple()
                )
                embed.set_footer(text=f"This curse will last for {hours}h")
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    self.logger.error(f"Failed to send mimic curse announcement: {e}")
        # Discord log for mimic purchase
        if self.log_func and self.log_guild:
            await self.log_func(
                self.log_guild,
                title="Mimic Purchased",
                details=f"{self.buyer.mention} placed a mimic curse on {self.target.mention} for {hours} hour(s). Nickname: '{self.nickname.value}'",
                color=discord.Color.orange()
            )






