from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

# Routes
from app.routes.upload import router as upload_router
from app.routes.history import router as history_router
from app.routes.analyze import router as analyze_router

# Charger les variables d'environnement (.env)
load_dotenv()

# Initialisation de l'app FastAPI
app = FastAPI(
    title="Accounting AI Agent",
    description="Upload accounting documents and receive smart insights.",
    version="1.0.0"
)

# Monter le dossier static situé à la racine
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclure les routes
app.include_router(analyze_router, tags=["Analysis"])
app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(history_router, tags=["History"])

# Route d'accueil
@app.get("/", response_class=HTMLResponse)
def home():
    html_path = Path(__file__).parent.parent / "static" / "index.html"
    return html_path.read_text(encoding="utf-8")
