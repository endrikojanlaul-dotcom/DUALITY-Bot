import discord
from discord.ext import commands
from ..config import config


class CloseView(discord.ui.View):
    """A small reusable view with a Close button that deletes the bot message.

    Only the original invoker (or a user with Manage Messages) can close/delete the message.
    """

    def __init__(self, author_id: int, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.author_id = author_id

    @discord.ui.button(label='Close', style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id and not getattr(interaction.user, 'guild_permissions', None) and not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("You can't close this.", ephemeral=True)
            return
        try:
            await interaction.message.delete()
        except Exception:
            try:
                await interaction.response.edit_message(view=None)
            except Exception:
                pass
        self.stop()


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
