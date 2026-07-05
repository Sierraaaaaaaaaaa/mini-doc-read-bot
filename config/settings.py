from __future__ import annotations

import os 
from dataclasses import dataclass
from urllib.parse import urlparse


from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    """
    A class to hold the application settings loaded from environment variables.
    """

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", 1500))
    OPENAI_TOP_P: float = float(os.getenv("OPENAI_TOP_P", 1.0))
    OPENAI_FREQUENCY_PENALTY: float = float(os.getenv("OPENAI_FREQUENCY_PENALTY", 0.0))
    OPENAI_PRESENCE_PENALTY: float = float(os.getenv("OPENAI_PRESENCE_PENALTY", 0.0))
    DEFAULT_BASE_URL: str = os.getenv("DEFAULT_BASE_URL", "https://support.optisigns.com")