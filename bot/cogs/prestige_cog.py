import discord
from discord.ext import commands
from ..services.prestige_service import compute_prestige
from ..db import get_session
from ..models import User


class PrestigeCog(commands.Cog):
    """Show prestige level for users."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='prestige', with_app_command=True)
    async def prestige(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        session = get_session()
        try:
            user = session.query(User).filter_by(discord_id=target.id).first()
            if not user:
                return await ctx.reply("No profile found for that user.")
            level = compute_prestige(user.lifetime_dep)
            await ctx.reply(f"{target.display_name} — Prestige {level} (lifetime DE-P: {user.lifetime_dep})")
        finally:
            session.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(PrestigeCog(bot))
