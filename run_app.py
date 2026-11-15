"""
TERRA-X Application Runner
Launches FastAPI backend serving REST endpoints and the MapLibre mission control frontend.
"""

import uvicorn
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from api.app import app

# Mount web directory
web_dir = Path(__file__).resolve().parent / "web"
if web_dir.exists():
    app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="web")

if __name__ == "__main__":
    print("=" * 70)
    print("TERRA-X: Planetary Surface Systems & Functional Analog Discovery Engine")
    print("NASA Space Apps 2026")
    print("Serving at: http://127.0.0.1:8000")
    print("=" * 70)
    uvicorn.run(app, host="127.0.0.1", port=8000)

