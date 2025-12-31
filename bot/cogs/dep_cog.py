import discord
from discord.ext import commands
from ..services.dep_service import add_kills, add_death, get_user_profile
from .utils_cog import CloseView
from ..services.rank_service import get_rank_by_dep


class DepCog(commands.Cog):
    """Commands to interact with DE-P system"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='kill', with_app_command=True)
    async def kill(self, ctx: commands.Context, member: discord.Member = None, amount: int = 1):
        """Record kill(s) for a user (hybrid)."""
        target = member or ctx.author
        gained = await add_kills(target.id, kills=max(1, amount))
        await ctx.reply(f"Recorded {amount} kill(s) for {target.display_name}. DE-P change: +{gained}")

    @commands.hybrid_command(name='death', with_app_command=True)
    async def death(self, ctx: commands.Context, member: discord.Member = None):
        """Record a death for a user."""
        target = member or ctx.author
        change = await add_death(target.id)
        await ctx.reply(f"Recorded death for {target.display_name}. DE-P change: {change}")

    @commands.hybrid_command(name='profile', with_app_command=True)
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        """Show a user's DE-P profile."""
        target = member or ctx.author
        data = await get_user_profile(target.id)
        if not data:
            return await ctx.reply("No profile found.")
        rank = get_rank_by_dep(data['dep'])
        embed = discord.Embed(title=f"{target.display_name} — Profile")
        embed.add_field(name='DE-P', value=str(data['dep']))
        embed.add_field(name='Rank', value=rank)
        embed.add_field(name='Lifetime DE-P', value=str(data['lifetime_dep']))
        embed.add_field(name='Kills', value=str(data['total_kills']))
        embed.add_field(name='Deaths', value=str(data['total_deaths']))
        embed.add_field(name='Prestige', value=str(data['prestige']))
        view = CloseView(ctx.author.id)
        await ctx.reply(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(DepCog(bot))
