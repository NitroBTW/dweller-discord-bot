# The Cavern Discord Bot

A feature-rich Discord bot custom-built for "The Cavern" Discord server. This bot brings together economy systems, casino games, moderation tools, and social features to create an engaging community experience.

> **Note:** This bot is specifically themed and configured for "The Cavern" Discord server. While the code is open source, many features and themes are tailored to this particular community.

## Features

### Economy System
- **Daily Rewards**: Claim daily gold with streak bonuses
- **Balance Tracking**: Check your gold balance anytime
- **Shop System**: Purchase special items like Mimic's Curse and Barrel Time
- **Activity Rewards**: Earn gold by participating in server discussions

### Casino Games
- **Blackjack**: Play against the dealer with a full interactive interface
- **Roulette**: Bet on numbers, colors, or odds/evens
- **Slots**: Try your luck on the slot machine
- **Leaderboards**: See who has the most gold and best win rates

### Social Features
- **Welcome/Goodbye**: Automated greetings for new and departing members
- **Color Roles**: Customize your name color in the server
- **Whisper System**: Send anonymous messages to a designated channel
- **Intro Sticky**: Persistent intro template in the introductions channel
- **User Tiers**: Level up system based on message activity

### Moderation Tools
- **Warning System**: Issue and track user warnings
- **Setup Commands**: Configure bot channels and roles
- **Automatic Warning Expiry**: Old warnings automatically expire
- **Bump Reminders**: Server boost reminder system

### Server Management
- **Tier Roles**: Automatic role assignment based on activity
- **Channel Configuration**: Set up specific channels for different bot functions
- **Database Migration**: Automatic schema updates
- **Comprehensive Logging**: Full logging system for debugging and monitoring

## Installation

### Prerequisites
- Python 3.8 or higher
- A Discord application and bot token
- Discord server with appropriate permissions

### Step 1: Clone the Repository
```bash
git clone https://github.com/nitrobtw/dweller-discord-bot.git
cd dweller-discord-bot
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration
Create the `.env` file and add the following values:
   ```env
   # Discord Bot Configuration
   DISCORD_TOKEN=your_bot_token_here
   DEV_GUILD_ID=your_server_id_here
   ```

### Step 4: Discord Bot Setup
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token to your `.env` file
4. Invite the bot to your server with full permissions.

### Step 5: Run the Bot
```bash
python bot.py
```

## Bot Commands

### Economy Commands
- `/balance` - Check your current gold balance
- `/daily` - Claim your daily gold reward
- `/shop` - View available shop items
- `/buy` - Purchase items from the shop

### Game Commands
- `/games` - See available games
- `/blackjack <bet>` - Play blackjack against the dealer
- `/roulette <bet> <choice>` - Play roulette
- `/slots <bet>` - Play the slot machine
- `/leaderboard` - View server leaderboards

### Social Commands
- `/color <color>` - Set your name color
- `/whisper <message>` - Send an anonymous message
- `/help` - Display the help menu

### Moderation Commands (Admin only)
- `/setup` - Configure bot channels and roles
- `/warn <user> <reason>` - Issue a warning to a user
- Various configuration commands for channels and roles

## Database

The bot uses TinyDB (JSON-based database) to store:
- User profiles and statistics
- Server configurations
- Economy data
- Game statistics
- Moderation records

The database file is created automatically at `data/database.json`.

## Project Structure

```
cavern-discord-bot/
├── bot.py                 # Main bot file
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore file
├── README.md            # This file
├── cogs/                # Bot command modules
│   ├── Core/           # Core functionality
│   ├── Economy/        # Economy system
│   ├── Games/          # Casino games
│   └── Moderation/     # Moderation tools
├── utils/              # Utility modules
│   └── database.py     # Database handler
└── data/               # Data storage
    ├── database.json   # Main database (auto-created)
    └── logs/          # Log files
```

## Development

### Adding New Features
1. Create new cogs in the appropriate `cogs/` subfolder
2. Follow the existing code structure and commenting style
3. Add proper error handling and logging
4. Update the database schema if needed

### Database Schema
The bot automatically handles database migration. When adding new fields:
1. Update the default schemas in `utils/database.py`
2. Add migration logic in the `migrate_database()` method
3. The bot will automatically update existing data on startup

## License

This project is open source. Feel free to use and modify the code, but note that it's specifically themed for "The Cavern" Discord server.

## Disclaimer

This bot is custom-made for "The Cavern" Discord server. While the code is provided as-is, some features may not fit in other servers without modification of themes, channel references, and server-specific configurations.

This bot is custom-made for "The Cavern" Discord server. While the code is provided as-is, some features may not fit in other servers. This includes:
- Cave/underground themed language
- Server-specific references
- Features tailored to the server's tavern-in-a-cavern theme
- Integration with server-specific roles and channels