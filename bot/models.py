from sqlalchemy import Column, Integer, BigInteger, String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, unique=True, nullable=False)
    roblox_username = Column(String(100), nullable=True)
    dep = Column(Integer, default=0, nullable=False)
    lifetime_dep = Column(Integer, default=0, nullable=False)
    total_kills = Column(Integer, default=0, nullable=False)
    total_deaths = Column(Integer, default=0, nullable=False)
    prestige = Column(Integer, default=0, nullable=False)
    clan_joined_at = Column(DateTime, nullable=True)

    achievements = relationship('UserAchievement', back_populates='user')


class Achievement(Base):
    __tablename__ = 'achievements'
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(400), nullable=True)
    role_name = Column(String(200), nullable=True)


class UserAchievement(Base):
    __tablename__ = 'user_achievements'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    granted_at = Column(DateTime, server_default=func.now())

    user = relationship('User', back_populates='achievements')
    achievement = relationship('Achievement')

    __table_args__ = (UniqueConstraint('user_id', 'achievement_id', name='_user_achievement_uc'),)
