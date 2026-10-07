import json
import uuid

import streamlit as st

from src.config import get_settings, validate_settings
from src.graph import build_graph, save_approved_memory


st.set_page_config(page_title="Market Research Agent", page_icon="🔎", layout="wide")
st.title("🔎 Market Research Agent")
st.caption("LangGraph · Parallel Research · Human-in-the-Loop · LangSmith")


@st.cache_resource
def get_graph():
    settings = get_settings()
    errors = validate_settings(settings)
    if errors:
        raise RuntimeError("\n".join(errors))
    return build_graph(settings)


def reset():
    for key in ["thread_id", "company", "checkpoint_state", "report", "approved_json", "feedback"]:
        st.session_state.pop(key, None)


with st.sidebar:
    st.header("Configuration")
    settings = get_settings()
    st.write(f"**Model:** `{settings.model_provider}`")
    st.write(f"**LangSmith tracing:** `{settings.langsmith_tracing}`")
    if st.button("Reset demo"):
        reset()
        st.rerun()

st.markdown("**Workflow:** Orchestrator → 3 parallel Lead Researchers → Financial Analyst → 🛑 Human Review → Copywriter")

company = st.text_input(
    "Company or product to analyze",
    value=st.session_state.get("company", ""),
    placeholder="e.g. Notion, Slack, Canva",
)

if st.button("🚀 Start Research", type="primary", disabled=not company.strip()):
    errors = validate_settings(get_settings())
    if errors:
        st.error("\n".join(errors))
        st.stop()

    with st.spinner("Running orchestrator and parallel research..."):
        graph = get_graph()
        thread_id = str(uuid.uuid4())
        result = graph.invoke(
            {"company": company.strip()},
            {"configurable": {"thread_id": thread_id}},
        )

    st.session_state["thread_id"] = thread_id
    st.session_state["company"] = company.strip()
    st.session_state["checkpoint_state"] = result
    st.session_state["approved_json"] = json.dumps(result.get("structured_insights", {}), indent=2)
    st.session_state["feedback"] = ""
    st.success("Research complete. The graph is paused before Copywriter.")

if "checkpoint_state" in st.session_state:
    state = st.session_state["checkpoint_state"]

    st.divider()
    st.subheader("1. Orchestrator output")
    cols = st.columns(3)
    for i, competitor in enumerate(state.get("competitors", [])[:3]):
        with cols[i]:
            st.metric(f"Competitor {i + 1}", competitor)

    st.subheader("2. Parallel raw research")
    for item in state.get("raw_research", []):
        with st.expander(f"📄 {item.get('competitor', 'Unknown')}"):
            st.write(item.get("research", ""))

    st.subheader("3. Financial Analyst — human review")
    edited_json = st.text_area(
        "Edit the structured JSON if required.",
        value=st.session_state.get("approved_json", "{}"),
        height=500,
    )
    feedback = st.text_area(
        "Human reviewer feedback (optional)",
        value=st.session_state.get("feedback", ""),
        placeholder="Example: pricing appears stale; treat it as unverified.",
    )

    if st.button("✅ Approve & Generate Report", type="primary"):
        try:
            approved = json.loads(edited_json)
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")
            st.stop()

        thread_id = st.session_state["thread_id"]
        graph = get_graph()

        graph.update_state(
            {"configurable": {"thread_id": thread_id}},
            {
                "structured_insights": approved,
                "human_feedback": feedback,
                "human_approved": True,
            },
        )

        with st.spinner("Resuming graph → Copywriter..."):
            final_state = graph.invoke(
                None,
                {"configurable": {"thread_id": thread_id}},
            )

        st.session_state["checkpoint_state"] = final_state
        st.session_state["report"] = final_state.get("final_report", "")

        save_approved_memory(
            "streamlit-demo-user",
            st.session_state["company"],
            approved,
        )
        st.success("Human review accepted. Copywriter finished.")

if st.session_state.get("report"):
    st.divider()
    st.subheader("4. Final Competitive Analysis Briefing")
    st.markdown(st.session_state["report"])
    st.download_button(
        "⬇️ Download Markdown report",
        data=st.session_state["report"],
        file_name="competitive_analysis.md",
        mime="text/markdown",
    )
