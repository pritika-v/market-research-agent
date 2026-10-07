from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    model_provider: str
    openai_api_key: str
    openai_model: str
    groq_api_key: str
    groq_model: str
    openrouter_api_key: str
    openrouter_model: str
    ollama_model: str
    tavily_api_key: str
    langsmith_tracing: str
    langsmith_api_key: str
    langsmith_project: str
    langsmith_endpoint: str
    tavily_max_results: int
    orchestrator_mode: str


def get_settings() -> Settings:
    return Settings(
        model_provider=os.getenv("MODEL_PROVIDER", "openai").lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        ollama_model=os.getenv("OLLAMA_MODEL", "gemma4:12b"),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        orchestrator_mode=os.getenv("ORCHESTRATOR_MODE","llm"),
        groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash"),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        langsmith_tracing=os.getenv("LANGCHAIN_TRACING_V2", "false"),
        langsmith_api_key=os.getenv("LANGCHAIN_API_KEY", ""),
        langsmith_project=os.getenv("LANGCHAIN_PROJECT", "market-research-agent"),
        langsmith_endpoint=os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
        tavily_max_results=int(os.getenv("TAVILY_MAX_RESULTS", "5")),
    )


def validate_settings(settings: Settings) -> list[str]:
    errors = []
    if settings.model_provider == "openai" and not settings.openai_api_key:
        errors.append("OPENAI_API_KEY is missing.")
    if settings.model_provider == "openrouter" and not settings.openrouter_api_key:
        errors.append("OPENROUTER_API_KEY is missing.")
    if not settings.tavily_api_key:
        errors.append("TAVILY_API_KEY is missing.")
    return errors
