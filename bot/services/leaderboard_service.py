from typing import List, Tuple
from ..db import get_session
from ..models import User


def count_users() -> int:
    session = get_session()
    try:
        return session.query(User).count()
    finally:
        session.close()


def count_dep_entries() -> int:
    """Count users with DE-P > 0 for DEP leaderboard pagination."""
    session = get_session()
    try:
        return session.query(User).filter(User.dep > 0).count()
    finally:
        session.close()


def count_prestige_entries() -> int:
    """Count users with prestige > 0 for Prestige leaderboard pagination."""
    session = get_session()
    try:
        return session.query(User).filter(User.prestige > 0).count()
    finally:
        session.close()


def get_top_dep(limit: int = 10, offset: int = 0) -> List[Tuple[int, int]]:
    session = get_session()
    try:
        rows = session.query(User).order_by(User.dep.desc()).offset(offset).limit(limit).all()
        return [(r.discord_id, r.dep) for r in rows]
    finally:
        session.close()


def get_top_prestige(limit: int = 10, offset: int = 0):
    session = get_session()
    try:
        rows = session.query(User).order_by(User.prestige.desc(), User.lifetime_dep.desc()).offset(offset).limit(limit).all()
        return [(r.discord_id, r.prestige, r.lifetime_dep) for r in rows]
    finally:
        session.close()


def get_clan_roster_count() -> int:
    session = get_session()
    try:
        return session.query(User).count()
    finally:
        session.close()


def get_clan_roster_page(limit: int = 10, offset: int = 0) -> List[User]:
    session = get_session()
    try:
        rows = session.query(User).order_by(User.dep.desc()).offset(offset).limit(limit).all()
        return rows
    finally:
        session.close()
