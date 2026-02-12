import requests
import json

LM_API_URL = "http://127.0.0.1:1234" 


def generate_description(architecture_data: dict) -> str:
    prompt = (
        f"Generate a detailed technical architectural description for the following system.\n\n"
        f"Architecture ID: {architecture_data['architecture_id']}\n"
        f"Architecture Name: {architecture_data['architecture_name']}\n"
        f"Documentation Views: {', '.join(architecture_data['views'])}\n\n"
        f"Components:\n"
        f"{', '.join(architecture_data['components'])}\n\n"
        f"Relationships between components:\n"
        f"{', '.join([f'{r['source']} -> {r['target']}' for r in architecture_data['relationships']])}\n\n"
        f"Please describe the system's structure, components, and interactions clearly and concisely."
    )

    payload = {
        "model": "phi-2-layla-v1-chatml",  # Sostituisci con il modello corretto se necessario
        "prompt": prompt,
        "temperature": 0.7
    }

    # Usa l'endpoint '/v1/completions'
    response = requests.post(f"{LM_API_URL}/v1/completions", json=payload)

    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("text", "").strip()
    else:
        print(f"Error: {response.status_code}")
        return "No description generated."
