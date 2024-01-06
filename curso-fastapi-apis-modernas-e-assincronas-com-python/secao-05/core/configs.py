from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL: str = 'postgresql+asyncpg://admin:Password@localhost:5432/faculdade'

    class Config:
        case_sensitive = False


settings: Settings = Settings()
