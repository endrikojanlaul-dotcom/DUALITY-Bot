import math
import time
import discord
from discord.ext import commands
from ..services import leaderboard_service
from ..services.rank_service import get_rank_by_dep


class LeaderboardView(discord.ui.View):
    def __init__(self, bot: commands.Bot, kind: str, per_page: int, author_id: int, guild_id: int | None = None):
        super().__init__(timeout=120)
        self.bot = bot
        self.kind = kind.lower()
        self.per_page = per_page
        self.page = 1
        self.author_id = author_id
        self.guild_id = guild_id
        self._cache = {}  # page -> (embed, ts)
        # compute total pages where possible
        total_count = 0
        try:
            if self.kind == 'dep':
                total_count = leaderboard_service.count_dep_entries()
            elif self.kind == 'prestige':
                total_count = leaderboard_service.count_prestige_entries()
            else:
                total_count = leaderboard_service.count_users()
        except Exception:
            total_count = 0
        self.total_pages = max(1, math.ceil(total_count / self.per_page))

    async def get_embed(self):
        offset = (self.page - 1) * self.per_page
        embed = discord.Embed(color=discord.Color.blurple())

        # serve from cache when possible (short TTL)
        cached = self._cache.get(self.page)
        if cached and time.time() - cached[1] < 10:
            return cached[0]

        if self.kind == 'dep':
            # overfetch to skip bot accounts
            fetch_limit = max(self.per_page * 3, self.per_page + 5)
            rows = leaderboard_service.get_top_dep(limit=fetch_limit, offset=offset)
            embed.title = f"DE-P Leaderboard"
            embed.color = discord.Color.green()
            filtered = []
            for r in rows:
                if not await self._is_bot(r[0]):
                    filtered.append(r)
                if len(filtered) >= self.per_page:
                    break
            if filtered:
                desc_lines = [f"{i+1+offset}. <@{r[0]}> — **{r[1]:,}** DE-P" for i, r in enumerate(filtered)]
                embed.description = "\n".join(desc_lines)
            else:
                embed.description = "No entries."

        elif self.kind == 'prestige':
            fetch_limit = max(self.per_page * 3, self.per_page + 5)
            rows = leaderboard_service.get_top_prestige(limit=fetch_limit, offset=offset)
            embed.title = f"Prestige Leaderboard"
            embed.color = discord.Color.purple()
            filtered = []
            for r in rows:
                if not await self._is_bot(r[0]):
                    filtered.append(r)
                if len(filtered) >= self.per_page:
                    break
            if filtered:
                desc_lines = [f"{i+1+offset}. <@{r[0]}> — Prestige **{r[1]}** ({r[2]:,} lifetime DE-P)" for i, r in enumerate(filtered)]
                embed.description = "\n".join(desc_lines)
            else:
                embed.description = "No entries."

        elif self.kind == 'roster':
            rows = leaderboard_service.get_clan_roster_page(limit=self.per_page, offset=offset)
            embed.title = f"Clan Roster"
            embed.color = discord.Color.blue()
            # filter out bot members
            display_rows = []
            for r in rows:
                if not await self._is_bot(r.discord_id):
                    display_rows.append(r)
            if display_rows:
                desc_lines = [f"{i+1+offset}. <@{r.discord_id}> — {get_rank_by_dep(r.dep)} — {r.roblox_username or '—'}" for i, r in enumerate(display_rows)]
                embed.description = "\n".join(desc_lines)
            else:
                embed.description = "No members in roster."

        else:
            embed.title = "Unknown leaderboard"
            embed.description = "Use dep | prestige | roster"

        # footer with page info
        embed.set_footer(text=f"Page {self.page}/{self.total_pages}")
        # cache the embed briefly
        self._cache[self.page] = (embed, time.time())
        return embed

    async def _is_bot(self, discord_id: int) -> bool:
        # Try to resolve as guild member first (best), then cached user. If unknown, assume non-bot.
        try:
            if self.guild_id:
                g = self.bot.get_guild(self.guild_id)
                if g:
                    m = g.get_member(discord_id)
                    if m is not None:
                        return m.bot
            u = self.bot.get_user(discord_id)
            if u is not None:
                return getattr(u, 'bot', False)
        except Exception:
            pass
        return False

    async def update_message(self, interaction: discord.Interaction):
        embed = await self.get_embed()
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception:
            # fallback: send a followup
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # restrict control to the invoking user to avoid accidental button presses
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You didn't start this interaction.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label='◀️ Prev', style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("Already at first page.", ephemeral=True)

    @discord.ui.button(label='Next ▶️', style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # use precomputed total_pages
        if self.page < self.total_pages:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("No more pages.", ephemeral=True)

    @discord.ui.button(label='⏹️ Close', style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception:
            try:
                await interaction.response.edit_message(view=None)
            except Exception:
                pass
        self.stop()


class LeaderboardCog(commands.Cog):
    """Leaderboards for DE-P, prestige, and roster with embed pagination."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='leaderboard', with_app_command=True)
    async def leaderboard(self, ctx: commands.Context, kind: str = 'dep'):
        """Show leaderboards: dep | prestige | roster (embed paginator)."""
        view = LeaderboardView(self.bot, kind=kind, per_page=10, author_id=ctx.author.id)
        embed = await view.get_embed()
        await ctx.reply(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(LeaderboardCog(bot))
