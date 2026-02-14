import requests
import base64

LM_API_URL = "http://127.0.0.1:1234/v1/chat/completions"

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_diagram(image_path):
    image_base64 = encode_image(image_path)

    payload = {
        "model": "minicpm-v-2_6",  # metti esattamente il nome del tuo modello
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this UML diagram. Identify layout problems, duplicated elements, alignment issues, and visual inconsistencies."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.3
    }

    response = requests.post(LM_API_URL, json=payload)
    return response.json()