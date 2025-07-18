from fastapi import APIRouter, HTTPException
from pathlib import Path
import math
import json
from typing import Any, Dict, List, Union, cast

from app.services.extractor import read_document
from app.services.advisor import analyze_table_with_mistral, analyze_text_with_mistral
from app.utils.history import add_to_history

UPLOAD_DIR = Path("data/uploads")

router = APIRouter()

def sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj

@router.get("/analyze/{filename}")
async def analyze_existing_file(filename: str):
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        raw_data = read_document(str(file_path))
    except Exception as e:
        return {"message": f"Error while reading '{filename}'.", "error": str(e)}

    raw_data = sanitize(raw_data)

    if not isinstance(raw_data, dict) or "error" in raw_data:
        return {
            "message": f"Error while reading '{filename}'.",
            "error": raw_data["error"] if isinstance(raw_data, dict) and "error" in raw_data else "Invalid file format."
        }

    # ✅ cast typé pour éviter l’erreur Pyright
    preview_data: Dict[str, Any] = cast(Dict[str, Any], raw_data)
    preview_rows: List[Dict[str, Any]] = preview_data.get("preview", [])

    gpt_analysis: str = "⚠️ Aucune donnée analysable."

    try:
        if preview_rows and isinstance(preview_rows[0], dict) and "Date" in preview_rows[0]:
            gpt_analysis = analyze_table_with_mistral(preview_data)
        elif preview_rows and isinstance(preview_rows[0], dict) and "Texte extrait" in preview_rows[0]:
            texte = preview_rows[0].get("Texte extrait", "")
            if isinstance(texte, str):
                gpt_analysis = analyze_text_with_mistral(texte)
            else:
                gpt_analysis = "❌ Texte OCR mal extrait."
        else:
            gpt_analysis = "❌ Aucune structure exploitable détectée dans le fichier."
    except Exception as e:
        gpt_analysis = f"⚠️ GPT analysis failed: {str(e)}"
        print("GPT ERROR:", e)

    gpt_analysis_sanitized = sanitize(gpt_analysis)

    try:
        columns = preview_data.get("columns")
        if not isinstance(columns, list):
            columns = list(columns.values()) if isinstance(columns, dict) else []

        if not isinstance(gpt_analysis_sanitized, str):
            gpt_analysis_sanitized = json.dumps(gpt_analysis_sanitized, ensure_ascii=False, indent=2)

        add_to_history(filename, columns, gpt_analysis_sanitized)
    except Exception as e:
        print("History saving failed:", e)

    try:
        json.dumps({
            "message": f"File '{filename}' analyzed successfully.",
            "excel_preview": preview_data,
            "analysis": gpt_analysis_sanitized
        })
    except Exception as e:
        return {
            "message": "⚠️ Internal error: JSON serialization failed.",
            "error": str(e)
        }

    return {
        "message": f"File '{filename}' analyzed successfully.",
        "excel_preview": preview_data,
        "analysis": gpt_analysis_sanitized
    }
