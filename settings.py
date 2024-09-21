from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()


class Settings(BaseSettings):
    api_token: str
    instance_id: str

    model_config = SettingsConfigDict(env_file=".env")
