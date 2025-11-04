"""
Application configuration management.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    api_title: str = "LLM Test Generator"
    api_version: str = "0.1.0"
    api_description: str = "Generate and grade educational tests using LLMs"

    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"  # Lightweight model for testing
    openai_base_url: str | None = None

    # Generation defaults
    default_total_questions: int = 20
    default_single_choice_ratio: float = 0.7
    default_multiple_choice_ratio: float = 0.3

    # Output settings
    output_dir: str = "out"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
