import discord
from discord.ext import commands
from ..config import config


class UtilsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='suggest', with_app_command=True)
    async def suggest(self, ctx: commands.Context, *, suggestion: str):
        """Send a suggestion to the configured channel."""
        chan_id = config.SUGGESTIONS_CHANNEL_ID
        if not chan_id:
            return await ctx.reply("Suggestions channel not configured.")
        channel = ctx.guild.get_channel(chan_id) if ctx.guild else self.bot.get_channel(chan_id)
        if channel is None:
            return await ctx.reply("Suggestions channel not found on this server.")
        embed = discord.Embed(title='Suggestion', description=suggestion, color=discord.Color.blue())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await channel.send(embed=embed)
        await ctx.reply("Suggestion submitted. Thank you!")

    @commands.hybrid_command(name='bug', with_app_command=True)
    async def bug(self, ctx: commands.Context, *, report: str):
        chan_id = config.BUGS_CHANNEL_ID
        if not chan_id:
            return await ctx.reply("Bugs channel not configured.")
        channel = ctx.guild.get_channel(chan_id) if ctx.guild else self.bot.get_channel(chan_id)
        if channel is None:
            return await ctx.reply("Bugs channel not found on this server.")
        embed = discord.Embed(title='Bug Report', description=report, color=discord.Color.red())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await channel.send(embed=embed)
        await ctx.reply("Bug reported. Thank you!")


async def setup(bot: commands.Bot):
    await bot.add_cog(UtilsCog(bot))
