"""
Configuration management for AI Sandbox applications.

This module handles environment-based configuration with validation.
Follows Principle 2: Convention Over Configuration.

Environment Variables:
    ENVIRONMENT: "local" | "dev" | "preprod" | "prd" (default: "local")
    DATABASE_URL: PostgreSQL connection string
    AI_PROVIDER: "mock" | "ollama" | "openai" (default: "mock")
    AI_BASE_URL: Base URL for AI service (for Ollama)
    OPENAI_API_KEY: API key for OpenAI (if using OpenAI)

Local Development:
    - Uses ENVIRONMENT=local
    - AI_PROVIDER=mock (no real AI calls)
    - DATABASE_URL points to local Docker PostgreSQL

Server Deployment:
    - Change ENVIRONMENT to "dev", "preprod", or "prd"
    - Change AI_PROVIDER to "ollama"
    - Change AI_BASE_URL to Ollama server (e.g., http://192.168.1.102:11434)
    - Update DATABASE_URL to server PostgreSQL (e.g., postgresql://user:pass@192.168.1.101:5432/dbname)

See LOCAL_DEVELOPMENT.md for complete migration guide.
"""

import os
from typing import Literal
from pydantic import BaseModel, Field, validator
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    """
    Application configuration with validation.

    Follows Principle 6: Type Safety and Structured Data.
    Uses Pydantic for automatic validation of environment variables.
    """

    environment: Literal["local", "dev", "preprod", "prd"] = Field(
        default="local",
        description="Deployment environment"
    )

    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/ai_sandbox",
        description="PostgreSQL connection string"
    )

    ai_provider: Literal["mock", "ollama", "openai"] = Field(
        default="mock",
        description="AI provider to use"
    )

    ai_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for Ollama (ignored for mock/openai)"
    )

    openai_api_key: str = Field(
        default="",
        description="OpenAI API key (only needed if ai_provider=openai)"
    )

    ai_model: str = Field(
        default="llama3.1:8b",
        description="AI model name (llama3.1:8b for Ollama, gpt-4o-mini for OpenAI)"
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level"
    )

    @validator("openai_api_key")
    def validate_openai_key(cls, v, values):
        """Validate OpenAI API key is present when using OpenAI provider."""
        if values.get("ai_provider") == "openai" and not v:
            raise ValueError("OPENAI_API_KEY required when AI_PROVIDER=openai")
        return v

    @validator("ai_model")
    def set_default_model(cls, v, values):
        """Set appropriate default model based on provider."""
        provider = values.get("ai_provider")

        # If user didn't specify a model, use provider-appropriate default
        if v == "llama3.1:8b":  # Default value
            if provider == "openai":
                return "gpt-4o-mini"
            elif provider == "ollama":
                return "llama3.1:8b"
            elif provider == "mock":
                return "mock-model"

        return v

    class Config:
        """Pydantic config."""
        env_prefix = ""  # Load from environment variables directly


def load_config() -> AppConfig:
    """
    Load and validate configuration from environment variables.

    Returns:
        AppConfig: Validated configuration object

    Raises:
        ValidationError: If configuration is invalid

    Example:
        >>> config = load_config()
        >>> print(f"Using {config.ai_provider} in {config.environment}")
        Using mock in local
    """
    try:
        config = AppConfig(
            environment=os.getenv("ENVIRONMENT", "local"),
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql://postgres:postgres@localhost:5432/ai_sandbox"
            ),
            ai_provider=os.getenv("AI_PROVIDER", "mock"),
            ai_base_url=os.getenv("AI_BASE_URL", "http://localhost:11434"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            ai_model=os.getenv("AI_MODEL", "llama3.1:8b"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

        logger.info(f"Configuration loaded successfully")
        logger.info(f"Environment: {config.environment}")
        logger.info(f"AI Provider: {config.ai_provider}")
        logger.info(f"AI Model: {config.ai_model}")

        return config

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


def is_local() -> bool:
    """Check if running in local development environment."""
    return os.getenv("ENVIRONMENT", "local") == "local"


def is_production() -> bool:
    """Check if running in production environment."""
    return os.getenv("ENVIRONMENT", "local") == "prd"


# Global config instance (lazy loaded)
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """
    Get global configuration instance (singleton pattern).

    Returns:
        AppConfig: Global configuration object

    Example:
        >>> from shared.config import get_config
        >>> config = get_config()
        >>> if config.ai_provider == "mock":
        ...     print("Using mock AI for testing")
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config
