from pathlib import Path
import re

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from .config import get_settings

settings = get_settings()

tavily = TavilySearch(
    max_results=settings.tavily_max_results,
    topic="general",
)


REFERENCE_DIR = Path(__file__).resolve().parent.parent / "data" / "reference_docs"


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


@tool
def search_web(query: str) -> str:
    """Search the web for current information about a competitor."""

    results = tavily.invoke({
        "query": query
    })

    formatted = []

    for result in results.get("results", []):
        title = result.get("title", "")
        url = result.get("url", "")
        content = result.get("content", "")

        content = content[:2000]

        formatted.append(
            f"TITLE: {title}\n"
            f"URL: {url}\n"
            f"CONTENT:\n{content}"
        )

    return "\n\n---\n\n".join(formatted)


@tool
def search_reference_docs(query: str) -> str:
    """Search local Markdown/text market research documents."""
    if not REFERENCE_DIR.exists():
        return "No reference document directory exists."

    terms = [t.lower() for t in re.findall(r"[a-zA-Z0-9]+", query) if len(t) > 2]
    matches = []

    for path in REFERENCE_DIR.rglob("*"):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        lower = content.lower()
        score = sum(lower.count(term) for term in terms)
        if score:
            matches.append((score, path, content))

    matches.sort(key=lambda x: x[0], reverse=True)

    if not matches:
        return "No relevant local reference documents found."

    return "\n\n---\n\n".join(
        f"FILE: {path.name}\nRELEVANCE_SCORE: {score}\nCONTENT:\n{_clean(content)[:6000]}"
        for score, path, content in matches[:5]
    )
