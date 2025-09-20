from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "olKAN"
    debug: bool = False

settings = Settings()
