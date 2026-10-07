from typing import Any

from langgraph.constants import END, START, Send
from langgraph.graph import StateGraph

from .agents import (
    build_agents,
    invoke_analyst,
    invoke_copywriter,
    invoke_lead_researcher,
    invoke_orchestrator,
)
from .config import Settings
from .memory import checkpointer, store
from .state import ResearchState


def build_graph(settings: Settings):
    agents = build_agents(settings)

    def orchestrator_node(state: ResearchState) -> dict[str, Any]:
        return {
            "competitors": invoke_orchestrator(agents["orchestrator"], state["company"]),
            "human_approved": False,
        }

    def fan_out_research(state: ResearchState):
        return [
            Send(
                "lead_researcher",
                {"company": state["company"], "competitor": competitor},
            )
            for competitor in state["competitors"]
        ]

    def lead_researcher_node(state: dict[str, Any]) -> dict[str, Any]:
        item = invoke_lead_researcher(
            agents["lead_researcher"],
            state["company"],
            state["competitor"],
        )
        return {"raw_research": [item]}

    def analyst_node(state: ResearchState) -> dict[str, Any]:
        return {
            "structured_insights": invoke_analyst(
                agents["analyst"],
                state["company"],
                state.get("raw_research", []),
            )
        }

    def copywriter_node(state: ResearchState) -> dict[str, Any]:
        return {
            "final_report": invoke_copywriter(
                agents["copywriter"],
                state["company"],
                state.get("structured_insights", {}),
                state.get("human_feedback", ""),
            ),
            "human_approved": True,
        }

    builder = StateGraph(ResearchState)
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("lead_researcher", lead_researcher_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("copywriter", copywriter_node)

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges("orchestrator", fan_out_research)
    builder.add_edge("lead_researcher", "analyst")
    builder.add_edge("analyst", "copywriter")
    builder.add_edge("copywriter", END)

    return builder.compile(
        checkpointer=checkpointer,
        store=store,
        interrupt_before=["copywriter"],
    )


def save_approved_memory(user_id: str, company: str, structured_insights: dict):
    namespace = (user_id, "market_research")
    store.put(
        namespace,
        company.lower().replace(" ", "_"),
        {"company": company, "structured_insights": structured_insights},
    )
