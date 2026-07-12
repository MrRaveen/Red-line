from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    groq_api_key: str
    groq_model_id: str
    groq_base_url: str
    flask_env: str
    app_api_key: str
    log_level: str
    request_timeout_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
