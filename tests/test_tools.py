from src.tools import REFERENCE_DIR


def test_reference_directory_exists():
    assert REFERENCE_DIR.exists()


def test_sample_reference_document_exists():
    assert list(REFERENCE_DIR.glob("*.md"))
