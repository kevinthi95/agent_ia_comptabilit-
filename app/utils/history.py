import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("data/history.json")

def load_history():
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(history: list):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def add_to_history(filename: str, columns: list, analysis: str):
    history = load_history()
    history.append({
        "filename": filename,
        "upload_time": datetime.now().isoformat(),
        "preview_columns": columns,
        "gpt_analysis": analysis
    })
    save_history(history)
