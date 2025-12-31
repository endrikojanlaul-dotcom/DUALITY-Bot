from ..db import get_session
from ..models import Achievement, UserAchievement, User


DEFAULT_ACHIEVEMENTS = [
    ("novice_investor", "[D·Y] 🔷 Novice Investor", "Buy your first investment", None),
    ("arms_tycoon", "[D·Y] ♦️ Arms Tycoon", "Own multiple weapon factories", None),
    ("black_market", "[D·Y] ♠️ Black Market Dealer", "Trade in black market", None),
    ("lucky_shot", "[D·Y] ♣️ Lucky Shot", "Kill with 1 HP remaining", None),
    ("legendary_veteran", "[D·Y] 🔥 Legendary Veteran", "Long-time active member", None),
]


def ensure_default_achievements():
    session = get_session()
    try:
        for key, name, desc, role in DEFAULT_ACHIEVEMENTS:
            exist = session.query(Achievement).filter_by(key=key).first()
            if not exist:
                a = Achievement(key=key, name=name, description=desc, role_name=role)
                session.add(a)
        session.commit()
    finally:
        session.close()


def grant_achievement_to_user(discord_id: int, ach_key: str):
    """Grant an achievement to a user in the DB.

    Returns a tuple (success: bool, achievement or None, message: str).
    """
    session = get_session()
    try:
        user = session.query(User).filter_by(discord_id=discord_id).first()
        if not user:
            return False, None, "user_not_found"
        ach = session.query(Achievement).filter_by(key=ach_key).first()
        if not ach:
            return False, None, "achievement_not_found"
        exists = session.query(UserAchievement).filter_by(user_id=user.id, achievement_id=ach.id).first()
        if exists:
            return False, ach, "already_granted"
        ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
        session.add(ua)
        session.commit()
        return True, ach, "granted"
    finally:
        session.close()


def list_achievements():
    session = get_session()
    try:
        rows = session.query(Achievement).order_by(Achievement.id).all()
        return rows
    finally:
        session.close()
