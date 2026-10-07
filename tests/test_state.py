from typing import get_args, get_origin, Annotated
import operator
from src.state import ResearchState


def test_raw_research_uses_annotated_reducer():
    annotation = ResearchState.__annotations__["raw_research"]
    assert get_origin(annotation) is Annotated
    assert operator.add in get_args(annotation)[1:]
