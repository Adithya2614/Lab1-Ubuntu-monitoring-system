"""
WMI Backend Configuration Module
=================================
Loads all configuration from environment variables with sensible defaults.
Uses pydantic-settings for type-safe, validated configuration.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Defaults work for local development; override via .env file or env vars.
    """

    # --- Database ---
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://wmi_user:changeme@localhost:5432/wmi_db",
        description="PostgreSQL connection string (async driver)"
    )

    # Synchronous URL variant (for Alembic migrations)
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Convert async URL to sync for Alembic migrations."""
        return self.DATABASE_URL.replace("+asyncpg", "")

    # --- Ansible ---
    ANSIBLE_DIR: str = Field(
        default="./ansible",
        description="Path to ansible directory (relative to project root)"
    )
    ANSIBLE_VAULT_PASSWORD: str = Field(
        default="changeme",
        description="Password for Ansible Vault encryption/decryption"
    )

    @property
    def ANSIBLE_DIR_ABS(self) -> str:
        """Absolute path to the ansible directory."""
        return os.path.abspath(self.ANSIBLE_DIR)

    @property
    def INVENTORY_FILE(self) -> str:
        """Full path to the Ansible inventory hosts file."""
        return os.path.join(self.ANSIBLE_DIR_ABS, "inventory", "hosts")

    @property
    def PLAYBOOKS_DIR(self) -> str:
        """Full path to the Ansible playbooks directory."""
        return os.path.join(self.ANSIBLE_DIR_ABS, "playbooks")

    # --- WebSocket ---
    WS_PUSH_INTERVAL: int = Field(
        default=5,
        description="Seconds between periodic WebSocket metric pushes"
    )

    # --- Logging ---
    LOG_DIR: str = Field(
        default="./logs",
        description="Directory for log files (relative to project root)"
    )

    @property
    def LOG_DIR_ABS(self) -> str:
        """Absolute path to the log directory. Creates it if missing."""
        path = os.path.abspath(self.LOG_DIR)
        os.makedirs(path, exist_ok=True)
        return path

    # --- Security ---
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for signing tokens and sessions"
    )

    # --- Server ---
    BACKEND_HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    FRONTEND_URL: str = Field(
        default="http://localhost:5173",
        description="Frontend URL for CORS configuration"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    Call this instead of constructing Settings() directly so the .env
    file is only read once per process lifetime.
    """
    return Settings()
