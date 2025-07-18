import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
API_URL = "https://api.mistral.ai/v1/chat/completions"

if not API_KEY:
    raise ValueError("MISTRAL_API_KEY manquant")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def analyze_table_with_mistral(data: dict) -> str:
    try:
        lignes = data.get("preview", [])
        tableau_resume = "\n".join([
            f"{l['Date']} | {l['Libellé']} | -{l['Débit (€)'] or 0}€ / +{l['Crédit (€)'] or 0}€"
            for l in lignes if "Date" in l
        ])

        prompt = (
            "Tu es un expert-comptable. Voici des lignes d’un relevé bancaire :\n"
            f"{tableau_resume}\n"
            "➡️ Donne des conseils pour optimiser les dépenses et améliorer le rendement."
        )

        response = httpx.post(
            API_URL,
            headers=HEADERS,
            json={
                "model": "mistral-medium",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    except httpx.ReadTimeout:
        return "❌ L’analyse IA a dépassé le temps imparti. Réessaie plus tard ou simplifie les données."
    except Exception as e:
        return f"❌ Error during Mistral analysis: {str(e)}"


def analyze_text_with_mistral(text: str) -> str:
    try:
        prompt = (
            "Voici un bulletin de paie ou un document comptable :\n"
            f"{text}\n"
            "➡️ Fais une analyse financière ou comptable de ce document. Donne des conseils utiles."
        )

        response = httpx.post(
            API_URL,
            headers=HEADERS,
            json={
                "model": "mistral-medium",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

    except httpx.ReadTimeout:
        return "❌ Analyse trop longue. Réessaie plus tard."
    except Exception as e:
        return f"❌ Error during Mistral analysis: {str(e)}"
