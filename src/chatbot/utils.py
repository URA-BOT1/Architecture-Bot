from typing import Any, Dict


def extract_context(results: Dict[str, Any] | None) -> str:
    """Extract a context string from Chroma search results."""
    if not results:
        return ""
    docs = results.get("documents")
    if docs and len(docs) > 0 and docs[0]:
        # docs[0] is expected to be a list of strings
        return "\n".join(docs[0])
    return ""
