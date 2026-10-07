from pathlib import Path
from typing import Sequence

from langchain.agents import create_agent
from langchain_core.tools import BaseTool


SKILLS_ROOT = Path(__file__).resolve().parent.parent / "skills"


def load_skills(agent_slug: str) -> str:
    path = SKILLS_ROOT / agent_slug / "skills.md"
    if not path.exists():
        raise FileNotFoundError(f"Missing skills file: {path}")
    return path.read_text(encoding="utf-8")


def create_project_agent(
    *,
    name: str,
    description: str,
    system_prompt: str,
    tools: Sequence[BaseTool] | None,
    skills: str,
    model,
):
    """Project-specific wrapper around the current LangChain create_agent API."""
    combined_prompt = f"""
You are {name}.

ROLE:
{description}

SYSTEM INSTRUCTIONS:
{system_prompt}

SKILLS / WORKFLOW:
{skills}
""".strip()

    return create_agent(
        model=model,
        tools=list(tools or []),
        system_prompt=combined_prompt,
        name=name,
    )
