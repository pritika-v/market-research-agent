import operator
from typing import Annotated, TypedDict


class ResearchState(TypedDict, total=False):
    company: str
    competitors: list[str]
    raw_research: Annotated[list[dict], operator.add]
    structured_insights: dict[str, dict]
    human_approved: bool
    human_feedback: str
    final_report: str
