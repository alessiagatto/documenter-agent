import requests
import base64
from typing import Dict

LM_API_URL = "http://127.0.0.1:1234/v1/chat/completions"
DEFAULT_MODEL = "minicpm-v-2_6"

PROMPTS = {
    "sequence_diagram": (
        "Analyze this UML SEQUENCE diagram image. "
        "Check: missing/duplicated lifelines, message ordering, arrow direction, readability, spacing, and alignment. "
        "Return concrete fixes that can be applied in PlantUML (e.g., add actor User, reorder participants, avoid overlaps)."
    ),
    "component_diagram": (
        "Analyze this UML COMPONENT diagram image. "
        "Check: duplicated components, unclear dependencies, crossing lines, label overlap, inconsistent connector styles, layout readability. "
        "Return concrete PlantUML-oriented fixes (grouping, direction hints, simplification)."
    ),
    "deployment_diagram": (
        "Analyze this UML DEPLOYMENT diagram image. "
        "Check: node grouping, component-to-node mapping readability, overlaps, line crossings, label legibility. "
        "Return concrete PlantUML fixes (group nodes, rearrange, simplify connectors)."
    ),
    "context_diagram": (
        "Analyze this SYSTEM CONTEXT diagram image. "
        "Check: actors/external systems clarity, missing system boundary, overlaps, label readability, line crossings. "
        "Return concrete PlantUML fixes (system boundary, actor placement, simplified relations)."
    ),
    "security_diagram": (
        "Analyze this SECURITY diagram image (trust boundaries, threats, countermeasures). "
        "Check: clarity of boundaries, readability, overlaps, line crossings, consistent notation. "
        "Return concrete PlantUML fixes (grouping, boundary boxes, clearer labeling)."
    ),
}

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_diagram(image_path: str, diagram_type: str, model: str = DEFAULT_MODEL, timeout: int = 120) -> Dict:
    image_base64 = encode_image(image_path)

    prompt = PROMPTS.get(
        diagram_type,
        "Analyze this UML diagram image. Identify layout problems, duplicated elements, alignment issues, and visual inconsistencies. "
        "Return concrete fixes that can be applied in PlantUML."
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                ],
            }
        ],
        "temperature": 0.2,
    }

    try:
        response = requests.post(LM_API_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        # fallback “soft” output così non crasha tutto
        return {
            "choices": [
                {"message": {"content": "[VISION TIMEOUT] Nessun feedback disponibile (timeout)."}}
            ]
        }
    except requests.exceptions.RequestException as e:
        return {
            "choices": [
                {"message": {"content": f"[VISION ERROR] {e}"}}
            ]
        }