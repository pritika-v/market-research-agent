import sys
import uuid

from .config import get_settings, validate_settings
from .graph import build_graph


def main():
    company = " ".join(sys.argv[1:]).strip() or "Notion"
    settings = get_settings()
    errors = validate_settings(settings)
    if errors:
        raise SystemExit("\n".join(errors))

    graph = build_graph(settings)
    thread_id = str(uuid.uuid4())

    result = graph.invoke(
        {"company": company},
        {"configurable": {"thread_id": thread_id}},
    )

    print("=== HUMAN REVIEW CHECKPOINT ===")
    print("Thread:", thread_id)
    print("Competitors:", result.get("competitors"))
    print("Structured insights:", result.get("structured_insights"))
    print("Graph is paused before copywriter. Use Streamlit to approve/resume.")


if __name__ == "__main__":
    main()
