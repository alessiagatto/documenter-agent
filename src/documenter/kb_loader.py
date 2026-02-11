import json
from pathlib import Path


class KnowledgeBase:
    """
    Static Knowledge Base for documentation rules.
    """

    def __init__(self, kb_data: dict):
        self.view_to_diagram_mapping = kb_data.get("view_to_diagram_mapping", {})
        self.layout_rules = kb_data.get("layout_rules", {})


def load_knowledge_base(path: Path) -> KnowledgeBase:
    if not path.exists():
        raise FileNotFoundError(f"KB file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return KnowledgeBase(data)