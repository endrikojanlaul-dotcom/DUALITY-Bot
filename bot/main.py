import asyncio
import logging
import sys
import discord
from discord.ext import commands
from .config import config
from .logger import setup_logging, logger
from .db import init_db
from .services.achievement_service import ensure_default_achievements


def make_bot():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    bot.config = config
    return bot


async def load_all_cogs(bot: commands.Bot):
    # Load cogs via their setup functions
    cog_modules = [
        'bot.cogs.dep_cog',
        'bot.cogs.leaderboard_cog',
        'bot.cogs.admin_cog',
        'bot.cogs.utils_cog',
        'bot.cogs.achievements_cog',
        'bot.cogs.prestige_cog',
    ]
    for m in cog_modules:
        try:
            # load_extension may be a coroutine in this discord.py version; await it.
            await bot.load_extension(m)
            logger.info(f"Loaded cog {m}")
        except Exception as e:
            logger.exception(f"Failed to load cog {m}: {e}")


async def main():
    setup_logging()
    logger.info("Starting DUALITY bot")
    init_db()
    ensure_default_achievements()
    bot = make_bot()

    @bot.event
    async def on_ready():
        logger.info(f"Bot ready. Logged in as {bot.user} (ID: {bot.user.id})")

    await load_all_cogs(bot)

    try:
        await bot.start(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Shutting down (KeyboardInterrupt)")
        await bot.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception("Fatal error during startup", exc_info=e)
        sys.exit(1)
