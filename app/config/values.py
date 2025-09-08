"""nested model for settings."""

from enum import StrEnum

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class EnvironmentEnums(StrEnum):
    """enum for environment."""

    PRODUCTION = "PRODUCTION"
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"


class ConfigEnvironment(BaseSettings):
    """core config for environment."""

    environment: EnvironmentEnums = EnvironmentEnums.PRODUCTION
    name: str = "MKIT-AUTOUPDATEPRICE"
    debug: bool = False

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_env(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.upper()
        return v


class ConfigAppDatabase(BaseSettings):
    """Konfigurasi database untuk aplikasi."""

    url: str = "sqlite+aiosqlite:///./priceupdate.db"
    echo: bool = Field(
        default=False, description="Aktifkan logging SQL. Nonaktifkan untuk produksi."
    )

    timeout: int = Field(
        default=5, description="Waktu tunggu (detik) untuk koneksi database."
    )

    pool_size: int = Field(
        default=5, description="Jumlah koneksi yang disimpan dalam pool."
    )
    max_overflow: int = Field(
        default=10,
        description="Jumlah koneksi tambahan yang diizinkan saat pool penuh.",
    )


class ConfigOtomaxDB(BaseSettings):
    url: str = "mssql+pyodbc://localhost/otomax_db?driver=ODBC+Driver+17+for+SQL+Server"
    echo: bool = Field(
        default=False, description="Enable SQL logging. Disable for production."
    )
    timeout: int = Field(
        default=5, description="Timeout (seconds) for database connection."
    )
    pool_size: int = Field(
        default=5, description="Number of connections to keep in the pool."
    )
    max_overflow: int = Field(
        default=10,
        description="Number of additional connections allowed beyond the pool size.",
    )


class ConfigAdminAccount(BaseSettings):
    username: str = "admin"
    full_name: str = "Administrator"
    password: str = "admin123"
