import discord
from discord.ext import commands
from cogs.moderation.basemodcog import BaseModCog
from discord.ext.commands import check
from datetime import datetime

def can_warn():
    def predicate(ctx):
        if not isinstance(ctx.author, discord.Member):
            return False
        if ctx.author is ctx.guild.owner:
            return True
        return ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator
    return check(predicate)

def can_view_warnings():
    def predicate(ctx):
        return ctx.author.guild_permissions.manage_messages or ctx.author.guild_permissions.administrator
    return check(predicate)

class Warns(BaseModCog):
    def __init__(self, bot):
        super().__init__(bot, "Warns")

    @commands.hybrid_command(name="warn", usage="warn [user] [reason]", description="Warn a user in the server.")
    @can_warn()
    async def warn(self, ctx: commands.Context, target: discord.Member, *, reason: str = "No reason provided"):
        if target is None:
            await self.error(ctx, "Invalid target specified.")
            return

        if not await self.can_be_punished(ctx, target):
            return

        try:
            if ctx.guild is None:
                return
            await self.bot.db.add_warning(ctx.guild.id, target.id, ctx.author.id, reason)
            embed = discord.Embed(
                title="Warning Issued",
                description=f"**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
                color=self.basecolor
            )
            embed.add_field(name="Warned:", value=f"{target.mention} | ID: {target.id}", inline=False)
            await ctx.send(embed=embed)
            await self.mod_log(ctx, "Warning", target, reason)
        except Exception as e:
            await self.error(ctx, "Failed to record warning in the database.", e=e)

    @commands.hybrid_command(name="warnings", description="View all warnings for a user.")
    @can_view_warnings()
    async def view_warnings(self, ctx, member: discord.Member):
        """Fetch and display warnings for a specific user."""
        warnings = await self.bot.db.fetch_warnings(ctx.guild.id, member.id)
        if not warnings:
            await ctx.send(f"{member.display_name} has no warnings.")
            return

        # Building the response
        embed = discord.Embed(title=f"Warnings for {member.display_name}", color=discord.Color.red())
        for warn_id, issuer_id, reason, timestamp in warnings:
            issuer = await self.bot.fetch_user(issuer_id)  # Fetch the user who issued the warning
            issuer_name = issuer.display_name if issuer else "Unknown"
            formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            embed.add_field(
                name=f"Warning ID: {warn_id}",
                value=f"**Issuer:** {issuer_name}\n**Reason:** {reason}\n**Time:** {formatted_time}",
                inline=False
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Warns(bot))
