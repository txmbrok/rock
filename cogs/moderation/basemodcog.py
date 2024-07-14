import discord
from discord.ext import commands
from utils.logger import setup_discord_logger
from typing import Optional as Optional
import asyncio

# ! SET THESE:
logging_channel_id = 1261946962677338158

class BaseModCog(commands.Cog):
    def __init__(self, bot, cog_name):
        self.bot = bot
        self.cog_name = cog_name
        self.logger = setup_discord_logger()
        self.basecolor = 0x2F3136
        
        asyncio.create_task(self.delayed_channel_update())

    async def delayed_channel_update(self):
        await asyncio.sleep(11.0)
        await self.channel_update()

    async def channel_update(self):
        self.logging_channel = self.bot.get_channel(logging_channel_id)

        # Check if any channel object is None and print a warning
        if self.logging_channel is None:
            print("Warning: Some channels could not be found. Double-check the channel IDs.")

    async def answer(self, ctx, description):
        embed = discord.Embed(
            description=description,
            color=0x2F3136  # Base color for all logging messages
        )
        embed.set_author(name=f"{self.bot.user}", icon_url=ctx.bot.user.avatar.url)
        await ctx.send(embed=embed)

    async def logging(self, ctx, description, title: Optional[str] = "General Log"):
        if description is None:
            raise ValueError("Description must be provided for logging.")

        # Log to the bot's logger
        self.logger.debug(f"{ctx.author.display_name} ({ctx.author}) | {ctx.author.id} used {ctx.command.name} in {ctx.channel}, {ctx.guild}: {description}")
        
        # Check if the logging channel is set
        if self.logging_channel is None:
            print("Logging channel not set up yet. Skipping sending log message to Discord.")
            return

        # Send log message to the Discord channel
        embed = discord.Embed(
            title=title,
            description=description,
            color=0x2F3136
        )
        embed.set_footer(text=f"By: {ctx.author.display_name} ({ctx.author}) | {ctx.author.id}")
        await self.logging_channel.send(embed=embed)

    async def error(self, ctx, description: Optional[str] = None, *, e: Optional[Exception] = None, delete_after: Optional[int] = None, message: Optional[str] = None):
        if e and description is None:
            self.logger.error("Either description or Exception must be provided.")
        if e is not None:
            self.logger.error(description, exc_info=e)
        else:
            self.logger.error(description)
        embed = discord.Embed(
            title="An error occurred:",
            description=e or description,
            color=0xB32900
        )
        embed1 = embed
        embed1.set_author(name=self.bot.user.name, icon_url=ctx.bot.user.avatar.url)
        await ctx.send(content=message, embed=embed1, delete_after=delete_after)
        if self.logging_channel:
            embed.set_footer(text=f"Triggered by: {ctx.author.display_name} ({ctx.author}) | {ctx.author.id}")
            await self.logging_channel.send(embed=embed)

    async def can_be_punished(self, ctx: commands.Context, target: discord.Member) -> bool:
        if target.id is self.bot.user.id:
            return False
        if target.bot:
            await self.error(ctx, f"You can't moderate a bot!")
            return False
        if target.guild_permissions.administrator:
            await self.error(ctx, f"You can't moderate a administrator!")
            return False
        if target.top_role >= ctx.author.top_role:
            await self.error(ctx, f"You can't moderate someone with higher / same roles as you.")
            return False
        return True
        
        


async def setup(bot):
    cmd_prfx = bot.command_prefix
    await bot.add_cog(BaseModCog(bot, cmd_prfx))
