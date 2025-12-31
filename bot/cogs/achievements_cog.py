import discord
from discord.ext import commands
from ..services.achievement_service import list_achievements


class AchievementsCog(commands.Cog):
    """List achievements and view details."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='achievements', with_app_command=True)
    async def achievements(self, ctx: commands.Context):
        rows = list_achievements()
        if not rows:
            return await ctx.reply("No achievements configured.")
        embed = discord.Embed(title='Achievements')
        for a in rows:
            name = f"{a.name}"
            desc = a.description or '—'
            role = a.role_name or '—'
            embed.add_field(name=name, value=f"{desc}\nRole: {role}", inline=False)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(AchievementsCog(bot))
