import requests
import base64

LM_API_URL = "http://127.0.0.1:1234/v1/chat/completions"
VISION_MODEL = "minicpm-v-2_6"


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_diagram(image_path: str, diagram_type: str = "uml") -> dict:
    """
    Analizza un diagramma UML (immagine) con un Vision LLM.
    diagram_type: "sequence" | "component" | "deployment" | "context" | "security" | "uml"
    """
    image_base64 = encode_image(image_path)
    dt = (diagram_type or "uml").strip().lower()

    # Prompt vincolato: niente Mermaid, niente cambio tipo diagramma, solo feedback grafico/layout.
    text_prompt = f"""
You are a UML diagram reviewer.

Diagram type: {dt.upper()}.

Task:
- Provide ONLY layout/visual feedback (readability, alignment, spacing, overlaps, duplicated elements, arrow clarity, label placement, consistency).
- DO NOT change the diagram meaning/semantics.
- DO NOT propose Mermaid or any other notation.
- DO NOT rewrite the full diagram.
- DO NOT switch to a different UML diagram type.

Output format:
- Bullet list of concrete, actionable suggestions.
- If you detect duplicates, name them explicitly.
- If you suggest alignment changes, be specific (e.g., "order participants left-to-right: ...", "increase spacing between ...").
""".strip()

    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            }
        ],
        "temperature": 0.2,
    }

    response = requests.post(LM_API_URL, json=payload, timeout=180)
    try:
        response = requests.post(LM_API_URL, json=payload, timeout=180)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("[WARNING] Vision model timeout. Using original diagram.")
        return {"choices": [{"message": {"content": ""}}]}
    except Exception as e:
        print(f"[WARNING] Vision error: {e}")
        return {"choices": [{"message": {"content": ""}}]}

    response.raise_for_status()
    return response.json()