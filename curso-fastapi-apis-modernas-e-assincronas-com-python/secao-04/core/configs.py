from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base


class Settings(BaseSettings):
    """
    Configurações gerais utilizada na aplicação
    """

    API_VERSION: str = '/api/v1'
    DB_URL: str = 'postgresql+asyncpg://admin:Password@localhost:5432/faculdade'
    DBBaseModel = declarative_base()

    class Config:
        case_sensitive = False
        
settings = Settings()        
