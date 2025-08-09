import os
import discord
import logging
from datetime import datetime
from discord.ext import commands
from utils.database import Database
import colorlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging to both file and console
log_format = '[%(asctime)s] (%(name)s.%(funcName)s) %(log_color)s%(levelname)s: %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Ensure log directory exists
log_dir = os.path.join('data', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file_path = os.path.join(log_dir, f'{log_timestamp}.log')

# File handler (no color)
file_handler = logging.FileHandler(log_file_path, encoding="utf-8", mode="a")
file_handler.setFormatter(logging.Formatter('[%(asctime)s] (%(name)s.%(funcName)s) %(levelname)s:%(message)s', datefmt=date_format))

# Console handler (with color)
console_handler = colorlog.StreamHandler()
console_handler.setFormatter(colorlog.ColoredFormatter(
    log_format,
    datefmt=date_format,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'white',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Load configuration from environment variables
DEV_GUILD_ID = int(os.getenv('DEV_GUILD_ID'))

class Bot(commands.Bot):
    """
    Main bot class that handles Discord bot functionality.
    
    This bot is designed for "The Cavern" Discord server and includes
    features like economy systems, games, moderation tools, and social features.
    """
    
    def __init__(self):
        # Enable all intents for maximum functionality
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        # Initialize database connection
        self.db = Database()
        
    async def setup_hook(self):
        """
        Set up the bot by running database migration and loading all cogs.
        This runs once when the bot starts up.
        """
        # Run database migration to ensure schema is up to date
        self.db.migrate_database()
        logger.info("Database migration completed")
        
        # Load all cogs in logical groups
        logger.info("Loading bot extensions...")
        
        # Core functionality and help system
        await self.load_extension('cogs.Core.help')
        
        # Economy system - daily rewards, balance checking, shop
        await self.load_extension('cogs.Economy.daily')
        await self.load_extension('cogs.Economy.balance')
        await self.load_extension('cogs.Economy.shop')
        await self.load_extension('cogs.Economy.colour')
        
        # Gaming features - casino games and leaderboards  
        await self.load_extension('cogs.Games.roulette')
        await self.load_extension('cogs.Games.blackjack')
        await self.load_extension('cogs.Games.slots')
        await self.load_extension('cogs.Games.leaderboard')
        await self.load_extension('cogs.Games.barreltime')
        
        # Moderation tools and user management
        await self.load_extension('cogs.Moderation.moderation')
        await self.load_extension('cogs.Moderation.setup')
        await self.load_extension('cogs.Moderation.warning_expiry')
        
        # Social features and user engagement
        await self.load_extension('cogs.Core.greet')
        await self.load_extension('cogs.Core.introsticky')
        await self.load_extension('cogs.Core.tiers')
        await self.load_extension('cogs.Core.whisper')
        await self.load_extension('cogs.Core.bump')
        
        logger.info("All extensions loaded successfully")
        
    async def on_ready(self):
        """
        Event handler that runs when the bot successfully connects to Discord.
        Syncs slash commands and logs connection status.
        """
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info('------')

        # Sync application commands (slash commands) globally
        await self.tree.sync()
        logger.info("Successfully synced global commands")

def main():
    """
    Main entry point for the bot application.
    Loads environment variables, creates bot instance, and starts the bot.
    """
    # Create bot instance
    bot = Bot()
    
    # Get bot token from environment variables
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        logger.error("Please check your .env file and ensure DISCORD_TOKEN is set")
        return
    
    # Start the bot
    logger.info("Starting bot...")
    bot.run(token)

if __name__ == '__main__':
    main() 