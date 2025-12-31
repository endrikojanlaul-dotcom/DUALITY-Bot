import discord
from discord.ext import commands
from ..db import get_session
from ..models import User
from ..services.achievement_service import grant_achievement_to_user


def is_admin():
    def predicate(ctx: commands.Context):
        admin_role = ctx.bot.config.ADMIN_ROLE_NAME
        if ctx.guild is None:
            return False
        return any(r.name == admin_role for r in ctx.author.roles) or ctx.author.guild_permissions.administrator
    return commands.check(predicate)


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='setdep')
    @is_admin()
    async def setdep(self, ctx: commands.Context, member: discord.Member, amount: int):
        session = get_session()
        try:
            user = session.query(User).filter_by(discord_id=member.id).first()
            if not user:
                user = User(discord_id=member.id, dep=amount, lifetime_dep=max(0, amount))
                session.add(user)
            else:
                user.dep = amount
            session.commit()
            await ctx.reply(f"Set DE-P for {member.display_name} to {amount}")
        finally:
            session.close()

    @commands.command(name='grantach')
    @is_admin()
    async def grantach(self, ctx: commands.Context, member: discord.Member, key: str):
        success, ach, msg = grant_achievement_to_user(member.id, key)
        if not success:
            if msg == 'already_granted':
                await ctx.reply(f"{member.display_name} already has achievement `{key}`.")
            elif msg == 'achievement_not_found':
                await ctx.reply(f"Achievement `{key}` not found.")
            elif msg == 'user_not_found':
                await ctx.reply("User record not found in DB. Create profile first.")
            else:
                await ctx.reply("Failed to grant achievement.")
            return

        # Announce and attempt role assignment
        await ctx.reply(f"Granted achievement **{ach.name}** to {member.mention}.")
        # Assign role if configured
        if ach.role_name and ctx.guild:
            role = discord.utils.get(ctx.guild.roles, name=ach.role_name)
            if role:
                try:
                    await member.add_roles(role, reason=f"Achievement granted: {ach.key}")
                except Exception:
                    await ctx.reply("Granted achievement but failed to assign role (missing permissions)")


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
