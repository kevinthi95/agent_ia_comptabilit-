from fastapi import APIRouter
from app.utils.history import load_history

router = APIRouter()

@router.get("/history")
def get_history():
    return load_history()
