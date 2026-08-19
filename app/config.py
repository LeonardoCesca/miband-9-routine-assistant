from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")
    app_base_url: str = Field(default="", alias="APP_BASE_URL")
    app_timezone: str = Field(default="America/Sao_Paulo", alias="APP_TIMEZONE")
    scheduler_token: str = Field(default="", alias="SCHEDULER_TOKEN")

    miband_ble_address: str = Field(default="", alias="MIBAND_BLE_ADDRESS")
    miband_ble_name: str = Field(default="Xiaomi Smart Band 9 Pro", alias="MIBAND_BLE_NAME")
    miband_ble_debug: bool = Field(default=False, alias="MIBAND_BLE_DEBUG")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
