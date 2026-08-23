"""
config.py — OKF Bundle Agent Service Configuration
"""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Service configuration loaded from .env or environment variables."""

    # Service
    SERVICE_NAME: str = "okf-bundle-agent"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8002
    DEBUG: bool = False

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TIMEOUT: int = 30

    # Paths
    BUNDLE_ROOT: Path = Path(__file__).parent.parent / "okf_bundle"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
