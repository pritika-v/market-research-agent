from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from .config import Settings


def build_model(settings: Settings):

    # -------------------------
    # Ollama - Local Model
    # -------------------------
    if settings.model_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            temperature=0,
        )

    # -------------------------
    # Groq
    # -------------------------
    if settings.model_provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is required.")

        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0,
        )

    # -------------------------
    # OpenRouter
    # -------------------------
    if settings.model_provider == "openrouter":
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required.")

        return ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0,
        )

    # -------------------------
    # OpenAI
    # -------------------------
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required.")

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )