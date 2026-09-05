from  pydantic_settings  import BaseSettings


class Settings(BaseSettings):
    
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/yuz_tut"

    
    redis_url: str = "redis://redis:6379/0"

    
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()