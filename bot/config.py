import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN', '')
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./data/duality.db')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    SUGGESTIONS_CHANNEL_ID: int = int(os.getenv('SUGGESTIONS_CHANNEL_ID', '0'))
    BUGS_CHANNEL_ID: int = int(os.getenv('BUGS_CHANNEL_ID', '0'))
    ADMIN_ROLE_NAME: str = os.getenv('ADMIN_ROLE_NAME', '[D·Y] Staff')


config = Config()
