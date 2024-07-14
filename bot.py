import discord
from discord.ext import commands
from discord.ext.commands import check
import os
from dotenv import load_dotenv
import sys
from pathlib import Path
import asqlite
from asqlite_handler import Database

sys.path.insert(0, str(Path(__file__).parent))

class DB(commands.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all(), command_prefix='.', help_command=None)

    async def setup_hook(self):
        # Load the commands extension
        print("Running setup tasks")
        self.pool = await asqlite.create_pool(database="./database/database.db")
        


# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set intents for the bot
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.db = Database("./database/database.db")  # Assuming your DB file path

    async def setup_hook(self):
        await self.db.setup()
bot = MyBot()

# List to store enabled cogs
enabled_cogs = []

def cogsetup():
    def predicate(ctx):
        return ctx.author.id == 890960794337046532 or 897959178386145330 and isinstance(ctx.channel, discord.DMChannel)
    return check(predicate)

def hidden_command(name=None, **attrs):
    attrs['hidden'] = True
    return commands.command(name, **attrs) # type: ignore

async def load_extensions():
    base_path = './cogs'  # Base directory for cogs
    for root, dirs, files in os.walk(base_path):
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('__'):
                # Generate the full path for each file
                file_path = os.path.join(root, filename)
                # Generate the module name by removing the base directory and replacing os separators with dots
                module = file_path[len(base_path):].replace(os.sep, '.').removesuffix('.py')
                try:
                    await bot.load_extension('cogs' + module)
                    enabled_cogs.append('cogs' + module)
                    print(f"Successfully loaded cog: {module}")
                except Exception as e:
                    print(f"Failed to load extension {module}.\n{e}")



@hidden_command(name="cogenable")
@cogsetup()
async def enable(ctx, cog_name: str):
    if cog_name in enabled_cogs:
        await ctx.send(f"The cog '{cog_name}' is already enabled.")
    else:
        try:
            await bot.load_extension(f'cogs.{cog_name}')
            enabled_cogs.append(cog_name)  # Add the cog to the enabled_cogs list
            await ctx.send(f"Successfully enabled cog: {cog_name}")
        except Exception as e:
            await ctx.send(f"Failed to enable cog '{cog_name}'.\n{e}")

@hidden_command(name="cogdisable")
@cogsetup()
async def disable(ctx, cog_name: str):
    if cog_name not in enabled_cogs:
        await ctx.send(f"The cog '{cog_name}' is not enabled.")
    else:
        try:
            await bot.unload_extension(f'cogs.{cog_name}')
            enabled_cogs.remove(cog_name)
            await ctx.send(f"Successfully disabled cog: {cog_name}")
        except Exception as e:
            await ctx.send(f"Failed to disable cog '{cog_name}'.\n{e}")

@hidden_command(name="cogs")
@cogsetup()
async def cogs(ctx):
    cogs_list = ""
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py') and not cog.startswith('__'):
            cog_name = cog[:-3]
            if cog_name in enabled_cogs:
                cogs_list += f"- **{cog_name}**\n"
            else:
                cogs_list += f"- {cog_name}\n"
    if cogs_list:
        await ctx.send(f"Enabled and disabled cogs:\n{cogs_list}"
                    f"\n*Use cogenable or cogdisable to enable or disable certain cogs*")
    else:
        await ctx.send("No cogs found.")


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("Connected to the following guilds:")
    for guild in bot.guilds:
        print(f" - {guild.name} (id: {guild.id})")

async def main():
    await load_extensions()

    # Check if the token is correctly fetched
    if TOKEN is None:
        raise ValueError("The Discord bot token is not set. Please check your .env file.")

    # Start the bot with the given token
    try:
        await bot.start(TOKEN)
    except Exception as e:
        print(f"An error occurred while trying to log in or run the bot: {e}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
