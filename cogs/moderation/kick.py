import discord
from discord.ext import commands
from cogs.moderation.basemodcog import BaseModCog
from discord.ext.commands import check, MemberConverter

def can_kick():
    def predicate(ctx):
        if not isinstance(ctx.author, discord.Member):
            return False
        if ctx.author is ctx.guild.owner:
            return True
        return ctx.author.guild_permissions.kick_members or ctx.author.guild_permissions.administrator
    return check(predicate)

class Kick(BaseModCog):
    def __init__(self, bot):
        super().__init__(bot, "Kick")

    @commands.hybrid_command(name="kick", description="Kick a user from the server.")
    @commands.guild_only()  # Ensure command is used inside a server
    @can_kick()
    async def kick(self, ctx, target: discord.Member, *, reason: str = 'No reason provided'):
        if target is None:
            return

        if not await self.can_be_punished(ctx, target):
            return

        try:
            await ctx.guild.kick(target, reason=reason)
            embed = discord.Embed(
                title=f'{target.display_name} has been kicked.',
                color=0x7289DA,
                description=f"Kicked by {ctx.author.mention} for: {reason}"
            )
            await ctx.send(embed=embed)
            await self.logging(ctx, f"Kicked {target.display_name} (ID: {target.id})\nReason: {reason}")
        except Exception as e:
            await self.error(ctx, f"Failed to kick {target.display_name}: {str(e)}")

async def setup(bot):
    await bot.add_cog(Kick(bot))
