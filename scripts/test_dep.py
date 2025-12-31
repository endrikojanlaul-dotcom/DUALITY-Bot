import asyncio
import importlib

importlib.import_module('bot')
from bot.services.dep_service import add_kills, add_death, get_user_profile


async def main():
    user_id = 999999999999
    gained = await add_kills(user_id, kills=1)
    print('gained', gained)
    loss = await add_death(user_id)
    print('death change', loss)
    profile = await get_user_profile(user_id)
    print('profile', profile)


if __name__ == '__main__':
    asyncio.run(main())
