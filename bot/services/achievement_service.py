from ..db import get_session
from ..models import Achievement, UserAchievement, User


DEFAULT_ACHIEVEMENTS = [
    ("first_steps", "🔦 First Steps", "Start the game and build your base for the first time", "1417422241544540172"),
    ("weapons_magnate", "💎 Weapons Magnate", "Accumulate $1,000,000 in the game", "1417422476455186555"),
    ("gambling_club", "🎲 Gambling Club", "Buy your first box in the Black Market (for $250,000)", "1417422605215993967"),
    ("beginners_luck", "🍀 Beginner's Luck", "Get any weapon from your first purchased box", "1417422737982623754"),
    ("rebirth_master", "🏆 Rebirth Master", "Reach 5 rebirths (get the bunker)", "1417422857343860806"),
    ("hardened_veteran", "🛡 Hardened Veteran", "Reach 15 rebirths", "1417422950931365940"),
    ("vehicle_collector", "🚗 Vehicle Collector", "Purchase all vehicle types", "1417423091193348106"),
    ("speed_runner", "⚡️ Speed Runner", "Reach 3 rebirths within 24 hours", "1417423194171904102"),
    ("social_magnate", "🤝 Social Magnate", "Invite 10 friends to the server", "1417423393640288326"),
    ("server_veteran", "⭐️ Server Veteran", "Be an active member for more than 1 month", "1417423284366086194"),
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


def get_achievement_by_key(key: str):
    session = get_session()
    try:
        return session.query(Achievement).filter_by(key=key).first()
    finally:
        session.close()


def create_achievement(key: str, name: str, description: str = None, role_name: str = None):
    session = get_session()
    try:
        exist = session.query(Achievement).filter_by(key=key).first()
        if exist:
            return False, 'exists'
        a = Achievement(key=key, name=name, description=description, role_name=role_name)
        session.add(a)
        session.commit()
        return True, 'created'
    finally:
        session.close()


def delete_achievement(key: str) -> bool:
    session = get_session()
    try:
        a = session.query(Achievement).filter_by(key=key).first()
        if not a:
            return False
        session.delete(a)
        session.commit()
        return True
    finally:
        session.close()


def update_achievement(key: str, name: str = None, description: str = None, role_name: str = None) -> bool:
    session = get_session()
    try:
        a = session.query(Achievement).filter_by(key=key).first()
        if not a:
            return False
        changed = False
        if name is not None:
            a.name = name
            changed = True
        if description is not None:
            a.description = description
            changed = True
        if role_name is not None:
            a.role_name = role_name
            changed = True
        if changed:
            session.commit()
        return True
    finally:
        session.close()
