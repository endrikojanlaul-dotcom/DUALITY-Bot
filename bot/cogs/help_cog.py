import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    """Custom help command formatted as: Command / Command description // Example"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='help', with_app_command=True)
    async def help(self, ctx: commands.Context, command_name: str = None):
        """Show help for commands. Use `help <command>` for details."""
        entries = [
            ("/kill or !kill", "Record kill(s) for a user", "Example: /kill @User 2"),
            ("/death or !death", "Record a death for a user", "Example: /death @User"),
            ("/profile or !profile", "Show a user's DE-P profile", "Example: /profile @User"),
            ("/leaderboard or !leaderboard", "Show the DE-P/prestige/roster leaderboard", "Example: /leaderboard dep"),
            ("/achievements or !achievements", "List configured achievements", "Example: /achievements"),
            ("/prestige or !prestige", "Show prestige info for a user", "Example: /prestige @User"),
            ("/suggest or !suggest", "Send a suggestion to configured suggestions channel", "Example: /suggest Add new event"),
            ("/bug or !bug", "Report a bug to configured bugs channel", "Example: /bug NPCs not spawning"),
            ("Admin: /addach, /delach, /editach", "Create, delete, or edit achievements at runtime", "Example: /addach key 'Name' 'Description' 123456789012345678"),
        ]

        if command_name:
            # show details for a single command if it exists
            cmd = self.bot.get_command(command_name)
            if cmd:
                embed = discord.Embed(title=f"Help — {cmd.name}")
                embed.add_field(name="Signature", value=str(cmd), inline=False)
                embed.add_field(name="Help", value=cmd.help or "—", inline=False)
                await ctx.reply(embed=embed)
                return
            else:
                await ctx.reply("Command not found.")
                return

        embed = discord.Embed(title="DUALITY Commands", color=discord.Color.blurple())
        for name, desc, example in entries:
            embed.add_field(name=f"{name} / {desc}", value=f"// {example}", inline=False)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    # replace default help if present
    try:
        bot.remove_command('help')
    except Exception:
        pass
    await bot.add_cog(HelpCog(bot))
