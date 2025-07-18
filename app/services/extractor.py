import pandas as pd
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

def read_document(file_path: str, n_rows: int = 5) -> dict:
    try:
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
            df = df.where(pd.notnull(df), None)
            return {
                "columns": df.columns.tolist(),
                "preview": df.head(n_rows).to_dict(orient="records"),
                "num_rows": len(df)
            }

        elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return {
                "columns": ["Texte extrait"],
                "preview": [{"Texte extrait": text}],
                "num_rows": 1
            }

        elif file_path.endswith(".pdf"):
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])  # type: ignore[attr-defined]


            return {
                "columns": ["Texte extrait"],
                "preview": [{"Texte extrait": text}],
                "num_rows": 1
            }

        return {"error": "Format de fichier non pris en charge."}
    except Exception as e:
        return {"error": str(e)}
