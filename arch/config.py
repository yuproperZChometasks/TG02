#config.py
import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "7366611292:AAGOGiBaCRKuxOsZIuslKdOLZw9cNxY9Y3s")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/database.db")
    INCOMING_DIR: str = "data/incoming"
    OUTCOMING_DIR: str = "data/outcoming"

    class Config:
        env_file = ".env"

config = Config()