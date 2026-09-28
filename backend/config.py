from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8"
    )

    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    # Hindsight
    hindsight_base_url: str = "http://localhost:8888"
    hindsight_bank_id: str = "incident-memory"
    hindsight_api_llm_provider: str = "groq"
    hindsight_api_llm_api_key: str
    hindsight_api_llm_groq_service_tier: str = "on_demand"


def get_settings() -> Settings:
    return Settings()