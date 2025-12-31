import random
import asyncio
from typing import Optional
from sqlalchemy.orm import Session
from ..db import get_session
from ..models import User
from .rank_service import get_rank_by_dep, multiplier_for_rank


def _ensure_user(session: Session, discord_id: int) -> User:
    user = session.query(User).filter_by(discord_id=discord_id).first()
    if not user:
        user = User(discord_id=discord_id)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def _rand_range(min_v: int, max_v: int) -> int:
    return random.randint(min_v, max_v)


def calculate_kill_reward(kills: int) -> int:
    # For single kill: 3-15 per kill
    return sum(_rand_range(3, 15) for _ in range(kills))


def calculate_milestone_reward(total_kills: int) -> int:
    # milestones: 10 kills no death -> 30-150
    # 50 kills -> 150-750
    # 100 kills -> 300-1500
    reward = 0
    if total_kills >= 100:
        reward += _rand_range(300, 1500)
    elif total_kills >= 50:
        reward += _rand_range(150, 750)
    elif total_kills >= 10:
        reward += _rand_range(30, 150)
    return reward


async def add_kills(discord_id: int, kills: int = 1, consecutive_no_death: Optional[int] = None) -> int:
    loop = asyncio.get_event_loop()
    def _work():
        session = get_session()
        try:
            user = _ensure_user(session, discord_id)
            base = calculate_kill_reward(kills)
            user.total_kills += kills
            milestone = calculate_milestone_reward(user.total_kills)
            total = base + milestone
            rank_name = get_rank_by_dep(user.dep)
            mult = multiplier_for_rank(rank_name)
            total *= mult
            user.dep += total
            user.lifetime_dep += total
            session.commit()
            return total
        finally:
            session.close()
    return await loop.run_in_executor(None, _work)


async def add_death(discord_id: int) -> int:
    loop = asyncio.get_event_loop()
    def _work():
        session = get_session()
        try:
            user = _ensure_user(session, discord_id)
            loss = _rand_range(40, 90)
            rank_name = get_rank_by_dep(user.dep)
            mult = multiplier_for_rank(rank_name)
            loss *= mult
            user.dep = max(0, user.dep - loss)
            user.total_deaths += 1
            session.commit()
            return -loss
        finally:
            session.close()
    return await loop.run_in_executor(None, _work)


async def get_user_profile(discord_id: int) -> dict:
    loop = asyncio.get_event_loop()
    def _work():
        session = get_session()
        try:
            user = session.query(User).filter_by(discord_id=discord_id).first()
            if not user:
                return {}
            return {
                'discord_id': user.discord_id,
                'roblox_username': user.roblox_username,
                'dep': user.dep,
                'lifetime_dep': user.lifetime_dep,
                'total_kills': user.total_kills,
                'total_deaths': user.total_deaths,
                'prestige': user.prestige,
            }
        finally:
            session.close()
    return await loop.run_in_executor(None, _work)
