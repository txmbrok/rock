import discord
from discord.ext import commands
from cogs.moderation.basemodcog import BaseModCog
from humanfriendly import parse_timespan, InvalidTimespan
from datetime import timedelta
from discord.ext.commands import check

def can_warn():
    def predicate(ctx):
        if not isinstance(ctx.author, discord.Member):
            return False
        if ctx.author is ctx.guild.owner:
            return True
        return ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator
    return check(predicate)

class Warns(BaseModCog):
    def __init__(self, bot):
        super().__init__(bot, "Warns")

    @commands.hybrid_command()
    async def warn(self, ctx: commands.Context, target: discord.Member, message: str = "??"):
        if target is None:
            self.error(ctx, "kaputt")
        

async def setup(bot):
    await bot.add_cog(Warns(bot))

