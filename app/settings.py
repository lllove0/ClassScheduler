from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cancel_limit_minutes: int = 30


settings = Settings()
