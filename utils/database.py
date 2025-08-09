import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from tinydb import TinyDB, Query

class Database:
    """
    Database handler for The Cavern Discord bot.
    
    Manages all persistent data including user profiles, guild configurations,
    economy data, gaming statistics, and moderation records using TinyDB.
    """
    
    def __init__(self, db_file: str = "data/database.json"):
        self.db_file = db_file
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self.db = TinyDB(self.db_file)
        self.data = self._load_database()
        self.default_guild_schema = {
            "general_channel": None,
            "welcome_channel": None,
            "goodbye_channel": None,
            "whisper_channel": None,
            "log_channel": None,
            "intros_channel": None,
            "last_intro_id": None,
            "tier_1_role": None,
            "tier_2_role": None,
            "tier_3_role": None,
            "bump_role": None,
            "bot_channel": None,
            "colour_channel": None,
            "colour_roles": {},
            "users": {}
        }

        self.default_user_schema = {
            "warnings": [],
            "tier": 1,
            "message_count": 0,
            "gold": 0,
            "roulette_wins": 0,
            "roulette_losses": 0,
            "blackjack_wins": 0,
            "blackjack_losses": 0,
            "slots_wins": 0,
            "slots_losses": 0,
            "last_daily_claim": None,
            "streak": 0,
            "mimic_expiry": None,
            "barrel_expiry": None,
        }

        self.user_data_type_map = {
            "warnings": lambda v: [] if str(v).lower() == "none" or str(v).lower() == "[]" else eval(str(v)) if isinstance(v, str) else v,
            "tier": int,
            "message_count": int,
            "gold": int,
            "roulette_wins": int,
            "roulette_losses": int,
            "blackjack_wins": int,
            "blackjack_losses": int,
            "slots_wins": int,
            "slots_losses": int,
            "last_daily_claim": lambda v: None if str(v).lower() == "none" else str(v),
            "streak": int,
            "mimic_expiry": lambda v: None if str(v).lower() == "none" else str(v),
            "barrel_expiry": lambda v: None if str(v).lower() == "none" else str(v),
        }
    
    # Load the database from the JSON file, create it if it doesnt exist
    def _load_database(self) -> Dict[str, Any]:
        # TinyDB loads data automatically, so this is not needed
        # But for compatibility, we return a dict of all guilds
        data = {}
        for guild in self.db.all():
            data[guild["guild_id"]] = guild["data"]
        return data

    # Save any changes made to the database 
    def _save_database(self):
        # Save the current self.data to TinyDB
        self.db.truncate()
        for guild_id, guild_data in self.data.items():
            self.db.insert({"guild_id": guild_id, "data": guild_data})

    # Migrate the database to the latest schema
    def migrate_database(self):
        # Migrate guilds
        for guild_id in self.data:
            guild = self.data[guild_id]
            # Add any missing guild fields
            for key, value in self.default_guild_schema.items():
                if key not in guild:
                    guild[key] = value

            # Migrate users within each guild
            for user_id in guild["users"]:
                user = guild["users"][user_id]
                # Add any missing user fields
                for key, value in self.default_user_schema.items():
                    if key not in user:
                        user[key] = value
                
                # Migrate warnings from int to list if needed
                if "warnings" in user and isinstance(user["warnings"], int):
                    user["warnings"] = []

        self._save_database()
    
    # Get a guild's data from the database, create it if it doesn't exist
    def get_guild(self, guild_id: int) -> Dict[str, Any]:
        guild_id = str(guild_id)
        Guild = Query()
        result = self.db.get(Guild.guild_id == guild_id)
        if not result:
            self.data[guild_id] = self.default_guild_schema.copy()
            self._save_database()
            return self.data[guild_id]
        else:
            self.data[guild_id] = result["data"]
            return self.data[guild_id]
    
    # Get a user in a guild's data from the database, create it if it doesn't exist
    def get_user(self, guild_id: int, user_id: int) -> Dict[str, Any]:
        guild = self.get_guild(guild_id)
        user_id = str(user_id)
        if user_id not in guild["users"]:
            guild["users"][user_id] = self.default_user_schema.copy()
            self._save_database()
        return guild["users"][user_id]

    # Update a guild's data in the database 
    def update_guild_config(self, guild_id: int, **kwargs):
        guild = self.get_guild(guild_id)
        for key, value in kwargs.items():
            if key in guild:
                guild[key] = value
        self._save_database()
        
    # Update a user's data in the database
    def update_user(self, guild_id: int, user_id: int, **kwargs):
        user = self.get_user(guild_id, user_id)
        for key, value in kwargs.items():
            if key in user:
                user[key] = value
        self._save_database()

    # ~~~~~~~~~~ Intros ~~~~~~~~~~
    # Set the intros channel of a guild
    def set_intros_channel(self, guild_id: int, channel_id: int):
        guild = self.get_guild(guild_id)
        guild["intros_channel"] = str(channel_id)
        self._save_database()
    
    # Get a guild's intros channel
    def get_intros_channel(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["intros_channel"]
    
    # Set a guild's last template message id
    def set_intro_id(self, guild_id: int, message_id: int):
        guild = self.get_guild(guild_id)
        guild["last_intro_id"] = str(message_id)
        self._save_database()
    
    # Get a guild's last intro template message id
    def get_intro_id(self, guild_id: int):
        guild = self.get_guild(guild_id)
        message_id = guild["last_intro_id"]
        return message_id

    # ~~~~~~~~~~ Channels ~~~~~~~~~~
    # Set the general channel of a guild
    def set_general_channel(self, guild_id: int, channel_id: int):
        guild = self.get_guild(guild_id)
        guild["general_channel"] = str(channel_id)
        self._save_database()

    # Get a guild's general channel
    def get_general_channel(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["general_channel"]
    
    # Set the whisper channel of a guild
    def set_whisper_channel(self, guild_id: int, channel_id: int):
        guild = self.get_guild(guild_id)
        guild["whisper_channel"] = str(channel_id)
        self._save_database()
    
    # Get a guild's whisper channel
    def get_whisper_channel(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["whisper_channel"]

    # Set the welcome channel of a guild
    def set_welcome_channel(self, guild_id: int, channel_id: int):
        guild = self.get_guild(guild_id)
        guild["welcome_channel"] = str(channel_id)
        self._save_database()
    
    # Get a guild's welcome channel
    def get_welcome_channel(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["welcome_channel"]

    # Set the goodbye channel of a guild
    def set_goodbye_channel(self, guild_id: int, channel_id: int):
        guild = self.get_guild(guild_id)
        guild["goodbye_channel"] = str(channel_id)
        self._save_database()
    
    # Get a guild's goodbye channel
    def get_goodbye_channel(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["goodbye_channel"]
    
    # Set the log channel of a guild
    def set_log_channel(self, guild_id: int, channel_id: int):
        guild = self.get_guild(guild_id)
        guild["log_channel"] = str(channel_id)
        self._save_database()
    
    # Get a guild's log channel
    def get_log_channel(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["log_channel"]
    
    # Set a guild's bot channel
    def set_bot_channel(self, guild_id: int, channel_id: int):
        guild = self.get_guild(guild_id)
        guild["bot_channel"] = str(channel_id)
        self._save_database()

    # Get a guild's bot channel
    def get_bot_channel(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["bot_channel"]

    # Set the colour channel of a guild
    def set_colour_channel(self, guild_id: int, channel_id: int):
        guild = self.get_guild(guild_id)
        guild["colour_channel"] = str(channel_id)
        self._save_database()

    # Get a guild's colour channel
    def get_colour_channel(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["colour_channel"]

    # ~~~~~~~~~~ Tiers ~~~~~~~~~~
    # Add a message to the user
    def add_messages(self, guild_id: int, user_id: int, amount: int):
        user = self.get_user(guild_id, user_id)
        user["message_count"] += amount
        self._save_database()

    # Get a user's message count from the database
    def get_messages(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        count = user["message_count"]
        return count
    
    # Get a user's tier from the database
    def get_tier(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        tier = user["tier"]
        return tier
    
    # Get a guild's tier role based on int
    def get_tier_role(self, guild_id: int, tier: int):
        guild = self.get_guild(guild_id)
        role = guild[f"tier_{tier}_role"]
        return role
    
    # Set a user's tier in the database
    def set_tier(self, guild_id: int, user_id: int, tier: int):
        user = self.get_user(guild_id, user_id)
        user["tier"] = tier
        self._save_database()

    # Set a guild's tier role for a given tier
    def set_tier_role(self, guild_id: int, tier: int, role_id: int):
        guild = self.get_guild(guild_id)
        guild[f"tier_{tier}_role"] = str(role_id)
        self._save_database()

    # ~~~~~~~~~~ Gold ~~~~~~~~~~
    # Add gold to a user in a guild in the database
    def add_gold(self, guild_id: int, user_id: int, amount: int):
        user = self.get_user(guild_id, user_id)
        user["gold"] += amount
        self._save_database()
    
    # Remove gold from a user in a guild in the database
    def remove_gold(self, guild_id: int, user_id: int, amount: int):
        user = self.get_user(guild_id, user_id)
        user["gold"] -= amount
        self._save_database()

    # Get a user's gold from the database
    def get_user_gold(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        gold = user["gold"]
        return gold
    
    # Set a user in a guild's gold in the database
    def set_gold(self, guild_id: int, user_id: int, amount: int):
        user = self.get_user(guild_id, user_id)
        user["gold"] = amount
        self._save_database()
    
    # ~~~~~~~~~~ Daily ~~~~~~~~~~
    # Check if a user in a guild can claim a daily reward
    def can_claim_daily(self, guild_id: int, user_id: int) -> bool:
        user = self.get_user(guild_id, user_id)
        if not user["last_daily_claim"]:
            return True
            
        last_claim = datetime.fromisoformat(user["last_daily_claim"]).date()
        today = date.today()
        return last_claim < today
    
    # Set a user in a guild's last daily claim to the current time
    def claim_daily(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        user["last_daily_claim"] = datetime.now().isoformat()
        self._save_database()

    # Check if a user's streak should continue
    def can_increase_streak(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        if not user["last_daily_claim"]:
            return False
        
        last_claim = datetime.fromisoformat(user["last_daily_claim"]).date()
        yesterday = date.today() - timedelta(days=1)

        return last_claim == yesterday
    
    # Increase a user's streak
    def increase_streak(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        user["streak"] += 1
        self._save_database()

    # Get a user's streak
    def get_streak(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user["streak"]


    # ~~~~~~~~~~ Roulette ~~~~~~~~~~
    # Add a roulette win to a user in a guild in the database
    def add_roulette_wins(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        user["roulette_wins"] += 1
        self._save_database()

    # Add a roulette loss to a user in a guild in the database
    def add_roulette_losses(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        user["roulette_losses"] += 1
        self._save_database()

    # Get a user's wins on roulette in a guild from the database
    def get_roulette_wins(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user["roulette_wins"]

    # Get a user's losses on roulette in a guild from the database
    def get_roulette_losses(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user["roulette_losses"]


    # ~~~~~~~~~~ Blackjack ~~~~~~~~~~
    # Add a blackjack win to a user in a guild in the database
    def add_blackjack_wins(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        user["blackjack_wins"] += 1
        self._save_database()

    # Add a slots loss to a user in a guild in the database
    def add_blackjack_losses(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        user["blackjack_losses"] += 1
        self._save_database()

    # Get a user's wins on blackjack in a guild from the database
    def get_blackjack_wins(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user["blackjack_wins"]

    # Get a user's losses on blackjack in a guild from the database
    def get_blackjack_losses(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user["blackjack_losses"]
    
    # Get the user's wins and losses in blackjack
    def get_blackjack_winloss(self, guild_id: int, user_id: int):
        user_wins = self.get_blackjack_wins(guild_id, user_id)
        user_losses = self.get_blackjack_losses(guild_id, user_id)
        user_games = user_wins + user_losses
        user_winrate = round((user_wins / (user_games) * 100), 1) if user_games > 0 else 0
        return (user_wins, user_losses, user_winrate)
    
    # Set the last time the user played blackjack
    def set_blackjack_last_played(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        user["last_blackjack"] = datetime.now().isoformat()
        self._save_database()

    # ~~~~~~~~~~ Slots ~~~~~~~~~~
    # Add a slots win to a user in a guild in the database
    def add_slots_wins(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        user["slots_wins"] += 1
        self._save_database()

    # Add a slots loss to a user in a guild in the database
    def add_slots_losses(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        user["slots_losses"] += 1
        self._save_database()

    # Get a user's wins on slots in a guild from the database
    def get_slots_wins(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user["slots_wins"]


    # Get a user's losses on slots in a guild from the database
    def get_slots_losses(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user["slots_losses"]

    # ~~~~~~~~~~ Colour Roles ~~~~~~~~~~
    # Add a colour role to a guild
    def add_colour_role(self, guild_id: int, role_id: int, role_name: str):
        guild = self.get_guild(guild_id)
        guild["colour_roles"][str(role_id)] = role_name
        self._save_database()
    
    # Remove a colour role from a guild
    def remove_colour_role(self, guild_id: int, role_id: int):
        guild = self.get_guild(guild_id)
        if str(role_id) in guild["colour_roles"]:
            del guild["colour_roles"][str(role_id)]
            self._save_database()
    
    # Get all colour roles for a guild
    def get_colour_roles(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["colour_roles"]
    
    # Check if a role is a colour role
    def is_colour_role(self, guild_id: int, role_id: int):
        guild = self.get_guild(guild_id)
        return str(role_id) in guild["colour_roles"]

    # ~~~~~~~~~~ Bump Role ~~~~~~~~~~
    # Set the bump role of a guild
    def set_bump_role(self, guild_id: int, role_id: int):
        guild = self.get_guild(guild_id)
        guild["bump_role"] = str(role_id)
        self._save_database()
    
    # Get a guild's bump role
    def get_bump_role(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["bump_role"]

    # ~~~~~~~~~~ Mute Role ~~~~~~~~~~
    # Set the mute role of a guild
    def set_mute_role(self, guild_id: int, role_id: int):
        guild = self.get_guild(guild_id)
        guild["mute_role"] = str(role_id)
        self._save_database()
    
    # Get a guild's mute role
    def get_mute_role(self, guild_id: int):
        guild = self.get_guild(guild_id)
        return guild["mute_role"]

    # ~~~~~~~~~~ Shop ~~~~~~~~~~
    # Mimic expiry methods
    def set_mimic_expiry(self, guild_id: int, user_id: int, expiry: str):
        user = self.get_user(guild_id, user_id)
        user["mimic_expiry"] = expiry
        self._save_database()

    def get_mimic_expiry(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user.get("mimic_expiry")

    # Barrel time expiry
    def set_barrel_expiry(self, guild_id: int, user_id: int, expiry: str):
        user = self.get_user(guild_id, user_id)
        user["barrel_expiry"] = expiry
        self._save_database()

    def get_barrel_expiry(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user.get("barrel_expiry")

    # ~~~~~~~~~~ Set data ~~~~~~~~~~
    def set_user_data(self, guild_id: int, user_id: int, data_type: str, data_value: str):
        user = self.get_user(guild_id, user_id)
        converted_value = self.convert_user_data_type(data_type, data_value)
        user[f"{data_type}"] = converted_value
        self._save_database()

    def convert_user_data_type(self, key: str, value: str):
        func = self.user_data_type_map.get(key, str)
        return func(value)
    
    # ~~~~~~~~~~ Warnings ~~~~~~~~~~
    def add_warning(self, guild_id: int, user_id: int, reason: str):
        user = self.get_user(guild_id, user_id)
        warning_entry = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        }
        user["warnings"].append(warning_entry)
        self._save_database()

    def get_warnings(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return user.get("warnings", [])
    
    def get_warning_count(self, guild_id: int, user_id: int):
        user = self.get_user(guild_id, user_id)
        return len(user.get("warnings", []))