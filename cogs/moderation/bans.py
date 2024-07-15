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

    @commands.hybrid_command(name="ban", usage="ban [user] [reason]", description="Permanently ban a user from the server.")
    @can_ban()
    async def ban(self, ctx, target: discord.Member, *, reason: str = 'No reason provided'):
        if target is None:
            await self.error(ctx, "Invalid target specified.")
            return
        
        if not await self.can_be_punished(ctx, target):
            return

        try:
            await ctx.guild.ban(target, reason=reason)
            embed = discord.Embed(
                title="Ban Result",
                description=f"🔹 **Reason:** {reason}\n🔸 **Moderator:** {ctx.author.mention}",
                color=self.basecolor
            )
            embed.add_field(name="Banned:", value=f"{target.display_name} | ID: {target.id}", inline=False)
            await ctx.send(embed=embed)
            await self.logging(ctx, f"Banned {target.display_name} (ID: {target.id}) for: {reason}", "Ban Issued")
        except Exception as e:
            await self.error(ctx, "Failed to ban user.", e=e)

    @commands.hybrid_command(name="unban", usage="unban [user_id]", description="Unban a user from the server.")
    @can_ban()
    async def unban(self, ctx, target_id: int):
        try:
            user = discord.Object(id=target_id)
            await ctx.guild.unban(user)
            embed = discord.Embed(
                title="Unban Result",
                description=f"Successfully unbanned ID: {target_id}",
                color=self.basecolor
            )
            await ctx.send(embed=embed)
            await self.logging(ctx, f"Successfully unbanned {target_id}", "Unban Issued")
        except Exception as e:
            await self.error(ctx, "Failed to unban user.", e=e)

async def setup(bot):
    await bot.add_cog(Bans(bot))
