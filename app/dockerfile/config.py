# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"  # env_file 설정을 Config 클래스 안에 넣습니다.

settings = Settings()