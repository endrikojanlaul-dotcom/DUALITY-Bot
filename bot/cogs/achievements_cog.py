import discord
from discord.ext import commands
from ..services.achievement_service import list_achievements
from .utils_cog import CloseView


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
            role_display = '—'
            if a.role_name:
                # if numeric string, show mention
                try:
                    rid = int(a.role_name)
                    role_display = f"<@&{rid}>"
                except Exception:
                    role_display = a.role_name
            embed.add_field(name=name, value=f"{desc}\nRole: {role_display}", inline=False)
        view = CloseView(ctx.author.id)
        await ctx.reply(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AchievementsCog(bot))
