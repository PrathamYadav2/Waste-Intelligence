"""Central settings. Values come from environment / .env only; no dataset paths are hard-coded."""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    auth_mode: str = "placeholder"
    database_url: str = ""
    data_root: str = ""
    realwaste_path: str = ""
    trashnet_path: str = ""
    taco_path: str = ""
    regional_data_path: str = ""
    recovery_guidance_path: str = ""
    model_registry_dir: str = "models"

def get_settings() -> Settings:
    return Settings()
