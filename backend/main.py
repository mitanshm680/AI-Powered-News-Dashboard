from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import argparse, threading, sys

from backend.scheduler import start_scheduler
from backend.db.mongo import get_latest_articles
from tests.smoke_test import run_smoke_test
from backend.utils.logger import log

app = FastAPI(title="News Summary Dashboard Backend")

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Backend running"}

@app.get("/articles")
async def fetch_articles(limit: int = 20):
    try:
        return {"articles": get_latest_articles(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
def _startup():
    # fire‑and‑forget non‑blocking scheduler
    threading.Thread(target=start_scheduler, daemon=True).start()

# ---------- CLI ENTRY POINT -----------------------------------------------
def cli():
    parser = argparse.ArgumentParser(description="Run API server or smoke test")
    parser.add_argument("--smoke", action="store_true", help="Run smoke test & exit")
    args = parser.parse_args()

    if args.smoke:
        success = run_smoke_test()
        sys.exit(0 if success else 1)

    # If not smoke, start uvicorn server
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    cli()
