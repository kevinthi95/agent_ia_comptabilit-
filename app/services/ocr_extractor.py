import pytesseract
from PIL import Image

def extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)


### app/services/advisor.py
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
API_URL = os.getenv("MISTRAL_API_URL")

if not API_KEY or not API_URL:
    raise ValueError("MISTRAL_API_KEY ou MISTRAL_API_URL manquant")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def analyze_table_with_mistral(data: dict) -> str:
    try:
        prompt = (
            "Tu es un expert-comptable. Voici les données :\n"
            f"{json.dumps(data, ensure_ascii=False)}\n"
            "➡️ Donne des conseils pour optimiser les dépenses et améliorer le rendement."
        )

        response = httpx.post(API_URL or "", headers=HEADERS, json={
            "model": "accounts/mistral-7b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        })

        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Error during Mistral analysis: {str(e)}"