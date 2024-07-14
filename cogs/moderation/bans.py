import discord
from discord.ext import commands
from cogs.moderation.basemodcog import BaseModCog
from discord.ext.commands import check

def can_ban():
    def predicate(ctx):
        if not isinstance(ctx.author, discord.Member):
            return False
        if ctx.author is ctx.guild.owner:
            return True
        return ctx.author.guild_permissions.ban_members or ctx.author.guild_permissions.administrator
    return check(predicate)

class Bans(BaseModCog):
    def __init__(self, bot):
        super().__init__(bot, "Bans")


    @commands.hybrid_command(name="ban", usage="ban [user] [reason]", description="Ban a user from the server.")
    @can_ban()
    async def ban(self, ctx, target: discord.Member, *, reason: str = 'No reason given'):
        if target is None:
            await self.error(ctx, "Invalid target.")
            return
        
        if not await self.can_be_punished(ctx, target):
            return
        
        base_reason = f'Banned by {ctx.author.name}.'
        acc_reason = reason
        if reason == 'No reason given':
            acc_reason = base_reason

        try:
            await ctx.guild.ban(target, reason=acc_reason)

            embed = discord.Embed(
                title=f'{target} successfully banned.',
                color=self.basecolor,
                description=f"Banned by {ctx.author.mention}. Reason: {reason}"
            )
            await ctx.send(embed=embed)
            await self.logging(ctx, f"Successfully banned {target.id}\nReason: {reason}")
        except Exception as e:
            await self.error(ctx, e=e)


    @commands.hybrid_command(name="unban", usage="unban [user]", description="Unban a user from the server.")
    @can_ban()
    async def unban(self, ctx, target_id: int):
        try:
            await ctx.guild.unban(discord.Object(target_id))
            await self.answer(ctx, f"Successfully unbanned {target_id} from {ctx.guild}")
            await self.logging(ctx, f"Successfully unbanned `{target_id}`")
        except Exception as e:
            await self.error(ctx, f"Error occured while trying to unban `{target_id}`", e=e)


async def setup(bot):
    await bot.add_cog(Bans(bot))
