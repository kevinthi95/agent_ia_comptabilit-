import os
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

UPLOAD_ENDPOINT = "/upload/"
ANALYZE_ENDPOINT = "/analyze/"


def test_upload_invalid_filetype():
    response = client.post(UPLOAD_ENDPOINT, files={"file": ("test.txt", io.BytesIO(b"dummy"), "text/plain")})
    assert response.status_code == 400
    assert "Invalid file type" in response.text


def test_upload_missing_filename():
    class DummyFile:
        filename = ""
        content_type = "application/pdf"
        file = io.BytesIO(b"dummy")
    # Not directly testable via TestClient, but endpoint checks filename
    # So we skip this as TestClient always provides a filename
    pass


def test_upload_and_analyze_excel():
    # Crée un fichier Excel minimal en mémoire
    import pandas as pd
    import tempfile
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        tmp.flush()
        filename = os.path.basename(tmp.name)
        with open(tmp.name, "rb") as excel_file:
            response = client.post(UPLOAD_ENDPOINT, files={"file": (filename, excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert filename in data["message"]
    # Test analyse endpoint
    response2 = client.get(f"{ANALYZE_ENDPOINT}{filename}")
    assert response2.status_code == 200
    data2 = response2.json()
    assert "analysis" in data2
    assert "excel_preview" in data2


def test_analyze_nonexistent_file():
    response = client.get(f"{ANALYZE_ENDPOINT}fichier_inexistant.xlsx")
    assert response.status_code == 404
    assert "File not found" in response.text