from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    app_name: str = "olKAN"
    debug: bool = False
    storage_backend: str = "hybrid"
    data_dir: str = "data"

    @validator('debug', pre=True)
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v

settings = Settings()
