import requests
import json

LM_API_URL = "http://127.0.0.1:1234/v1/completions"
MODEL_NAME = "qwen2.5-coder-1.5b-instruct"


def extract_rules_from_feedback(diagram_type: str, vision_text: str) -> list:
    """
    Usa un LLM deterministico per estrarre regole strutturate dal feedback Vision.
    Restituisce una lista di rule names.
    """

    if not vision_text:
        return []

    prompt = f"""
You are a strict rule extractor.

Return ONLY valid JSON.
Do NOT explain.
Do NOT add text.

Output format:

{{
  "rules": ["rule_name"]
}}

Diagram type: {diagram_type}

Feedback:
{vision_text}
"""

    try:
        response = requests.post(
            LM_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "temperature": 0,
                "max_tokens": 80,
                "stop": ["```", "\n\n"]
            },
            timeout=20
        )

        data = response.json()

        # Controllo robusto
        if "choices" not in data:
            return []

        raw_text = data["choices"][0]["text"].strip()

        # Prova parsing JSON
        parsed = json.loads(raw_text)

        return parsed.get("rules", [])

    except Exception:
        # fallback sicuro
        return []