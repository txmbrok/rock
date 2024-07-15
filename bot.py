import discord
from discord.ext import commands
from utils.asqlite_handler import Database
import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    raise ValueError("The Discord bot token is not set. Please check your .env file.")

# Set up the bot class
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=".", intents=discord.Intents.all())
        self.db = Database("./database/database.db")  # Assuming your DB file path

    async def setup_hook(self):
        await self.db.setup()  # Set up the database
        await self.load_extensions()  # Load all extensions

    async def load_extensions(self):
        base_path = './cogs'  # Base directory for cogs
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                if filename.endswith('.py') and not filename.startswith('__'):
                    module = os.path.join(root, filename)[len(base_path):].replace(os.sep, '.').removesuffix('.py')
                    try:
                        await self.load_extension('cogs' + module)
                        print(f"Successfully loaded cog: {module}")
                    except Exception as e:
                        print(f"Failed to load extension {module}.\n{e}")

# Initialize the bot
bot = MyBot()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("Connected to the following guilds:")
    for guild in bot.guilds:
        print(f" - {guild.name} (id: {guild.id})")

if __name__ == '__main__':
    asyncio.run(bot.start(TOKEN))
