import discord
from discord.ext import commands
from cogs.moderation.basemodcog import BaseModCog
from discord.ext.commands import check

def can_manage_roles():
    def predicate(ctx):
        if not isinstance(ctx.author, discord.Member):
            return False
        if ctx.author is ctx.guild.owner:
            return True
        return ctx.author.guild_permissions.manage_roles or ctx.author.guild_permissions.administrator
    return check(predicate)

class RoleManagement(BaseModCog):
    def __init__(self, bot):
        super().__init__(bot, "RoleManagement")

    @commands.hybrid_command(name="role", description="Assign or remove a role from a user.")
    @commands.guild_only()  # Ensure command is used inside a server
    @can_manage_roles()
    async def role(self, ctx, target: discord.Member, *, role_name: str):
        """Give or remove a role from a member of the server."""
        if not role_name:
            await self.error(ctx, "You must specify a role name.")
            return

        role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), ctx.guild.roles)
        if role is None:
            await self.error(ctx, f"No role named '{role_name}' found.")
            return

        if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            await self.error(ctx, "You do not have permission to manage this role due to role hierarchy.")
            return

        if role in target.roles:
            try:
                await target.remove_roles(role)
                embed = discord.Embed(
                    title="Role Removed",
                    description=f"{role.name} was removed from {target.display_name}.",
                    color=self.basecolor
                )
                await ctx.send(embed=embed)
                await self.logging(ctx, f"Role {role.name} removed from {target.display_name} by {ctx.author.display_name}.")
            except Exception as e:
                await self.error(ctx, f"Failed to remove role: {str(e)}")
        else:
            try:
                await target.add_roles(role)
                embed = discord.Embed(
                    title="Role Assigned",
                    description=f"{role.name} was assigned to {target.display_name}.",
                    color=self.basecolor
                )
                await ctx.send(embed=embed)
                await self.logging(ctx, f"Role {role.name} assigned to {target.display_name} by {ctx.author.display_name}.")
            except Exception as e:
                await self.error(ctx, f"Failed to assign role: {str(e)}")

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
