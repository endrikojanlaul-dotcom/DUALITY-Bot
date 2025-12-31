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
        # Assign role if configured; support role id, mention, or name
        if ach.role_name and ctx.guild:
            role = None
            # try numeric id
            try:
                rid = int(ach.role_name)
                role = ctx.guild.get_role(rid)
            except Exception:
                # try to extract id from mention
                try:
                    import re
                    m = re.search(r"(\d+)", ach.role_name)
                    if m:
                        role = ctx.guild.get_role(int(m.group(1)))
                except Exception:
                    role = None

            # fallback to name lookup
            if role is None:
                role = discord.utils.get(ctx.guild.roles, name=ach.role_name)

            if role:
                try:
                    await member.add_roles(role, reason=f"Achievement granted: {ach.key}")
                except Exception:
                    await ctx.reply("Granted achievement but failed to assign role (missing permissions)")

    @commands.command(name='addach')
    @is_admin()
    async def addach(self, ctx: commands.Context, key: str, name: str, *, description: str = None):
        """Add a new achievement. Usage: !addach key "Name" Description"""
        from ..services.achievement_service import create_achievement
        ok, msg = create_achievement(key, name, description)
        if ok:
            await ctx.reply(f"Achievement `{key}` created.")
        else:
            await ctx.reply(f"Failed to create achievement: {msg}")

    @commands.command(name='delach')
    @is_admin()
    async def delach(self, ctx: commands.Context, key: str):
        """Delete an achievement by key."""
        from ..services.achievement_service import delete_achievement
        ok = delete_achievement(key)
        if ok:
            await ctx.reply(f"Achievement `{key}` deleted.")
        else:
            await ctx.reply(f"Achievement `{key}` not found.")

    @commands.command(name='editach')
    @is_admin()
    async def editach(self, ctx: commands.Context, key: str, field: str, *, value: str):
        """Edit an achievement field. Fields: name | description | role"""
        from ..services.achievement_service import update_achievement
        field = field.lower()
        if field not in ('name', 'description', 'role'):
            return await ctx.reply("Field must be one of: name, description, role")
        kwargs = {}
        if field == 'name':
            kwargs['name'] = value
        elif field == 'description':
            kwargs['description'] = value
        elif field == 'role':
            kwargs['role_name'] = value
        ok = update_achievement(key, **kwargs)
        if ok:
            await ctx.reply(f"Achievement `{key}` updated.")
        else:
            await ctx.reply(f"Achievement `{key}` not found.")

    @commands.command(name='listach')
    @is_admin()
    async def listach(self, ctx: commands.Context):
        """List all achievements with keys (admin view)."""
        from ..services.achievement_service import list_achievements
        rows = list_achievements()
        if not rows:
            return await ctx.reply("No achievements configured.")
        embed = discord.Embed(title='Achievements (admin)')
        for a in rows:
            embed.add_field(name=f"{a.key} — {a.name}", value=a.description or '—', inline=False)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
