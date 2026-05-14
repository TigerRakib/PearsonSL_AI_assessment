from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Doc RAG Pipeline"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    upload_dir: str = "uploads"
    max_file_size_mb: int = 50



settings = Settings()
