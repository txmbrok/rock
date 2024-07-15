import discord
from discord.ext import commands
from cogs.moderation.basemodcog import BaseModCog
from humanfriendly import parse_timespan, InvalidTimespan
from datetime import timedelta, datetime
from discord.ext.commands import check

def can_timeout():
    def predicate(ctx):
        if not isinstance(ctx.author, discord.Member):
            return False
        if ctx.author is ctx.guild.owner:
            return True
        return ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator
    return check(predicate)

class Mutes(BaseModCog):
    def __init__(self, bot):
        super().__init__(bot, "Mutes")

    @commands.hybrid_command(name="timeout", aliases=["mute", "timeout_add"], usage="mute [user] [duration] [reason]", description="Temporarily mute a user in the server.")
    @can_timeout()
    async def mute(self, ctx, target: discord.Member, duration: str, *, reason: str = 'No reason.'):
        if target is None:
            await self.error(ctx, "Invalid target.")
            return
        
        if not await self.can_be_punished(ctx, target):
            return
        
        if target.is_timed_out():
            await self.error(ctx, f"{target.display_name} is currently timeouted.")
            return

        try:
            real_duration = parse_timespan(duration)
            timeout_until = discord.utils.utcnow() + timedelta(seconds=real_duration)
            await target.edit(timed_out_until=timeout_until, reason=reason)
            embed = discord.Embed(
                title="Timeout",
                color=self.basecolor,
                description=f"**Reason:** {reason}\n**Moderator:** {ctx.author.mention}\n**Duration:** `{duration}`"
            )
            embed.add_field(name="Timed out:", value=f"    {target.name} | `{target.id}`" )
            await ctx.send(embed=embed)
            await self.mod_log(ctx, "Timeout", target, reason)
        except InvalidTimespan:
            await self.error(ctx, f"Invalid duration provided: `{duration}`")
        except Exception as e:
            await self.error(ctx, e=e)

    @commands.hybrid_command(name="untimeout", aliases=["unmute", "timeout_remove"], usage="unmute [user]", description="Unmute a user in the server.")
    @can_timeout()
    async def unmute(self, ctx, target: discord.Member):
        if target is None:
            await self.error(ctx, "Invalid target.")
            return

        if not target.is_timed_out():
            await self.error(ctx, f"{target.display_name} is not currently muted.")
            return

        try:
            await target.edit(timed_out_until=None, reason="Timeout removed by" + str(ctx.author))
            embed = discord.Embed(
                title="Unmute",
                color=self.basecolor,
                description=f"**Moderator:** {ctx.author.mention}\n**Target:** {target.name} | `{target.id}`"
            )
            await ctx.send(embed=embed)
            await self.mod_log(ctx, "Timeout removed", target, "Timeout removed by " + str(ctx.author))
        except Exception as e:
            await self.error(ctx, e=e)

async def setup(bot):
    await bot.add_cog(Mutes(bot))
