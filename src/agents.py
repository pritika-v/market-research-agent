import json
from .config import get_settings
from typing import Any

from .agent_factory import create_project_agent, load_skills
from .model import build_model
from .tools import search_reference_docs, search_web


def _text(result: dict[str, Any]) -> str:
    messages = result.get("messages", [])
    if not messages:
        return ""
    content = messages[-1].content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", str(block)) if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


def build_agents(settings):
    model = build_model(settings)

    orchestrator = create_project_agent(
        name="orchestrator",
        description="Plans the research job and identifies the strongest three competitors.",
        system_prompt="""Given a company or product, identify exactly three meaningful competitors.
Use web search when useful. Exclude the target itself.
Return ONLY valid JSON:
{"competitors": ["Competitor 1", "Competitor 2", "Competitor 3"]}""",
        tools=[search_web],
        skills=load_skills("orchestrator"),
        model=model,
    )

    lead_researcher = create_project_agent(
        name="lead_researcher",
        description="Collects evidence for one competitor using current web search and local reference documents.",
        system_prompt="""
        You are a Lead Researcher researching exactly one competitor.

        Use the available web search and reference-document tools.

        Your job is NOT to reproduce the retrieved documents.

        Instead:

        1. Read the retrieved information.
        2. Extract only decision-useful facts.
        3. Remove duplicate information.
        4. Ignore irrelevant details.
        5. Return concise evidence for the Analyst.

        Prioritize:
        - pricing
        - features
        - target customers
        - market positioning
        - competitive advantages
        - recent news/developments

        Keep every finding short.

        Never copy large sections of webpages.

        The final response must be concise and structured using:

        Competitor:
        Pricing:
        Features:
        Market Positioning:
        Recent Developments:
        Competitive Advantages:
        Sources:

        Limit the response to approximately 500-800 words maximum.
        """,
        tools=[search_web, search_reference_docs],
        skills=load_skills("lead_researcher"),
        model=model,
    )

    analyst = create_project_agent(
        name="financial_analyst",
        description="Transforms raw competitive research into structured evidence-backed insights.",
        system_prompt="""Read the raw research in the user message and create JSON keyed by competitor.
Include pricing, features, positioning, target_customers, recent_news, strengths, weaknesses,
evidence_quality and sources. Use Not found rather than inventing missing information.""",
        tools=[],
        skills=load_skills("financial_analyst"),
        model=model,
    )

    copywriter = create_project_agent(
        name="copywriter",
        description="Turns approved structured competitive intelligence into an executive briefing.",
        system_prompt="""Write a polished Markdown competitive analysis with executive summary,
comparison tables, competitor analysis, pricing, features, positioning, recent news,
strategic takeaways and sources. Only use approved data.""",
        tools=[],
        skills=load_skills("copywriter"),
        model=model,
    )

    return {
        "orchestrator": orchestrator,
        "lead_researcher": lead_researcher,
        "analyst": analyst,
        "copywriter": copywriter,
    }


def invoke_orchestrator(agent, company: str) -> list[str]:
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"Find the top 3 competitors for: {company}"
        }]
    })

    raw = _text(result)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")

        if start < 0 or end <= start:
            raise ValueError("Orchestrator did not return JSON.")

        data = json.loads(raw[start:end + 1])

    competitors = data["competitors"]

    if len(competitors) != 3:
        raise ValueError(
            "Orchestrator must return exactly three competitors."
        )

    return [str(x).strip() for x in competitors]


def invoke_lead_researcher(agent, company: str, competitor: str) -> dict:
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"Target: {company}\nResearch competitor: {competitor}. Perform the full skills workflow.",
        }]
    })
    return {"competitor": competitor, "company": company, "research": _text(result)}


def invoke_analyst(agent, company: str, raw_research: list[dict]) -> dict:
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": (
                f"Target company/product: {company}\n\nRAW PARALLEL RESEARCH:\n"
                f"{json.dumps(raw_research, indent=2)}\n\nReturn ONLY valid JSON."
            ),
        }]
    })
    raw = _text(result)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("Financial Analyst did not return valid JSON.")
        return json.loads(raw[start:end + 1])


def invoke_copywriter(agent, company: str, structured_insights: dict, human_feedback: str) -> str:
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": (
                f"Target: {company}\n\nAPPROVED DATA:\n"
                f"{json.dumps(structured_insights, indent=2)}\n\n"
                f"HUMAN FEEDBACK:\n{human_feedback or 'None'}\n\n"
                "Write the final Markdown briefing."
            ),
        }]
    })
    return _text(result)
