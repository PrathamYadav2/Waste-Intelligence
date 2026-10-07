"""Entry point: serves the API and the static frontend in app/. Run: python app.py"""
import uvicorn
from src.config import get_settings

if __name__ == "__main__":
    s = get_settings()
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=s.app_env == "development")
