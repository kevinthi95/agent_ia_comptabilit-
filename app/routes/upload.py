from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
from pathlib import Path
import os
import pandas as pd

from app.services.extractor import read_document
#from app.services.ocr_extractor import extract_text_from_image
from app.services.advisor import analyze_table_with_mistral
from app.utils.history import add_to_history

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()

def secure_filename(filename: str) -> str:
    return os.path.basename(filename)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    print("Received file:", file.filename)

    if not file.content_type in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/png",
        "image/jpeg"
    ]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing.")

    safe_filename = secure_filename(file.filename)
    file_location = UPLOAD_DIR / safe_filename

    if not file_location.exists():
        try:
            with open(file_location, "wb") as f:
                shutil.copyfileobj(file.file, f)
            print("File saved:", file_location)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    else:
        print(f"File '{safe_filename}' already exists. Reusing existing file.")

    preview = read_document(str(file_location))

    if "error" in preview:
        return {
            "message": f"File '{safe_filename}' found but reading failed.",
            "error": preview["error"]
        }

    try:
        analysis_result = analyze_table_with_mistral(preview)
    except Exception as e:
        analysis_result = f"⚠️ Mistral analysis failed: {str(e)}"
        print("MISTRAL ERROR:", e)

    try:
        add_to_history(safe_filename, preview.get("columns", []), str(analysis_result))
    except Exception as e:
        print("History saving failed:", e)

    return {
        "message": f"File '{safe_filename}' analyzed (existing or new).",
        "preview": preview,
        "analysis": analysis_result
    }

@router.get("/files")
async def list_uploaded_files():
    try:
        files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")
