import json
from pathlib import Path

def update_kb_from_feedback(kb_path: Path, diagram_type: str, vision_text: str):

    if not kb_path.exists():
        return

    with open(kb_path, "r", encoding="utf-8") as f:
        kb = json.load(f)

    rules = kb.setdefault("diagram_quality_rules", {})
    diagram_rules = rules.setdefault(diagram_type, {})

    text = vision_text.lower()

    if "duplicate" in text:
        diagram_rules["no_duplicate_elements"] = True

    if "left to right" in text:
        diagram_rules["left_to_right_order"] = True

    if "spacing" in text:
        diagram_rules["increase_spacing"] = True

    if "alignment" in text:
        diagram_rules["improve_alignment"] = True

    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2)
