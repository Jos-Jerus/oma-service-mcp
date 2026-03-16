"""Settings for the OMA Service MCP Server."""

from typing import ClassVar, Any
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables with error handling
try:
    load_dotenv()
except FileNotFoundError:
    pass
except Exception as e:
    import warnings

    warnings.warn(f"Failed to load .env file: {e}")


class Settings(BaseSettings):
    """Configuration settings for the OMA Service MCP Server.

    Uses Pydantic BaseSettings to load and validate configuration from environment variables.
    """

    # MCP Server Configuration
    MCP_HOST: str = Field(
        default="0.0.0.0",
        json_schema_extra={
            "env": "MCP_HOST",
            "description": "Host address for the MCP server",
        },
    )
    MCP_PORT: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        json_schema_extra={
            "env": "MCP_PORT",
            "description": "Port number for the MCP server",
        },
    )

    # Transport Configuration
    TRANSPORT: Literal["sse", "streamable-http"] = Field(
        default="streamable-http",
        json_schema_extra={
            "env": "TRANSPORT",
            "description": "Transport protocol for the MCP server. "
            "Use 'streamable-http' for lightspeed-stack/Llama Stack integration, "
            "'sse' for IDE/stdio-based clients.",
        },
    )

    # Migration Planner API Configuration
    MIGRATION_PLANNER_URL: str = Field(
        default="http://localhost:7443",
        json_schema_extra={
            "env": "MIGRATION_PLANNER_URL",
            "description": "Migration Planner API base URL",
        },
    )

    # Authentication Configuration
    AUTH_TYPE: Literal["forwarded", "none"] = Field(
        default="none",
        json_schema_extra={
            "env": "AUTH_TYPE",
            "description": "Authentication type: "
            "'forwarded' to forward Authorization header from lightspeed-stack, "
            "'none' for no auth (local dev)",
        },
    )

    # Logging Configuration
    LOGGING_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        json_schema_extra={
            "env": "LOGGING_LEVEL",
            "description": "Logging level for the application",
        },
    )

    @field_validator("LOGGING_LEVEL", mode="before")
    @classmethod
    def _normalize_logging_level(cls, v: Any) -> Any:
        return v.upper() if isinstance(v, str) else v

    LOGGER_NAME: str = Field(
        default="",
        json_schema_extra={
            "env": "LOGGER_NAME",
            "description": "Name for the logger",
        },
    )

    LOG_TO_FILE: bool = Field(
        default=True,
        json_schema_extra={
            "env": "LOG_TO_FILE",
            "description": "Enable logging to file (disable in containers)",
        },
    )

    model_config: ClassVar[SettingsConfigDict] = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "validate_assignment": True,
        "frozen": False,
    }


def validate_config(cfg: Settings) -> None:
    """Validate configuration settings.

    Args:
        cfg: Settings instance to validate.

    Raises:
        ValueError: If required configuration is missing or invalid.
    """
    if not 1024 <= cfg.MCP_PORT <= 65535:
        raise ValueError(f"MCP_PORT must be between 1024 and 65535, got {cfg.MCP_PORT}")


# Create config instance
settings = Settings()


def get_setting(name: str) -> Any:
    """Return setting value, honoring runtime test patches."""
    if name in settings.__dict__:
        return settings.__dict__[name]
    return getattr(settings, name)
