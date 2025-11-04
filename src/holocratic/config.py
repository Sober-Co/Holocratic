"""Application configuration management for Holocratic."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="HOLOCRATIC_",
        env_file=".env",
        env_file_encoding="utf-8",
        validate_default=True,
    )

    postgres_url: PostgresDsn = Field(..., description="Primary Postgres connection string")
    redis_url: RedisDsn = Field(..., description="Redis connection string for caching and queues")

    multi_tenant_enabled: bool = Field(
        False,
        description="Toggle for enabling multi-tenant behaviour across the API.",
    )
    tenant_header: str = Field(
        "X-Tenant-ID",
        description="HTTP header used to resolve the current tenant context.",
    )
    tenant_cookie_name: str = Field(
        "tenant",
        description="Cookie used as a fallback for resolving the current tenant.",
    )
    default_tenant: str = Field(
        "public",
        description="Default tenant identifier when multi-tenancy is disabled or optional.",
    )
    enforce_tenant_presence: bool = Field(
        False,
        description="If true, requests without a tenant identifier are rejected.",
    )

    plugin_flags: Dict[str, bool] = Field(
        default_factory=dict,
        description=(
            "Mapping of plugin identifiers to their enabled state, configurable via the "
            "HOLOCRATIC_PLUGIN_FLAGS environment variable (e.g. 'chat=true,crm=false')."
        ),
    )

    api_host: str = Field("0.0.0.0", description="Network host for the ASGI server.")
    api_port: int = Field(8000, description="Network port for the ASGI server.")
    reload: bool = Field(False, description="Enable auto-reload (development only).")
    log_level: str = Field("info", description="Logging level for the ASGI server.")

    @field_validator("plugin_flags", mode="before")
    @classmethod
    def parse_plugin_flags(cls, value: object) -> Dict[str, bool]:
        if value in (None, "", {}):
            return {}
        if isinstance(value, dict):
            return {str(key): cls._to_bool(val) for key, val in value.items()}
        if isinstance(value, str):
            flags: Dict[str, bool] = {}
            for chunk in value.split(","):
                if not chunk.strip():
                    continue
                key, _, raw_value = chunk.partition("=")
                if not key:
                    continue
                cleaned_key = key.strip()
                if raw_value.strip() == "":
                    flags[cleaned_key] = True
                    continue
                flags[cleaned_key] = cls._to_bool(raw_value)
            return flags
        raise TypeError("plugin_flags must be a string or mapping")

    @staticmethod
    def _to_bool(value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            truthy = {"1", "true", "yes", "on", "enabled"}
            falsy = {"0", "false", "no", "off", "disabled"}
            if normalized in truthy:
                return True
            if normalized in falsy:
                return False
        raise ValueError(f"Cannot interpret value '{value}' as boolean.")

    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """Return True when the requested plugin is explicitly enabled."""

        return self.plugin_flags.get(plugin_name, False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    return Settings()


__all__ = ["Settings", "get_settings"]
