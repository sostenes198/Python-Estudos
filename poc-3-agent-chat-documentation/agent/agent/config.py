from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str
    openai_api_key: str
    mongodb_uri: str
    outline_base_url: str
    outline_api_token: str
    outline_webhook_secret: str
    slack_bot_token: str
    slack_signing_secret: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
