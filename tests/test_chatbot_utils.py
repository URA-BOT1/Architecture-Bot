import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from src.chatbot.utils import extract_context


def test_extract_context_empty():
    assert extract_context(None) == ""
    assert extract_context({}) == ""
    assert extract_context({"documents": []}) == ""
    assert extract_context({"documents": [[]]}) == ""


def test_extract_context_with_docs():
    results = {"documents": [["a", "b"]]}
    assert extract_context(results) == "a\nb"
