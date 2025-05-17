from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import threading

from backend.scheduler.scheduler import start_scheduler
from backend.db.mongo import get_latest_articles

app = FastAPI(title="News Summary Dashboard Backend")

# CORS setup — adjust origins for your frontend domain(s)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "News Summary Dashboard Backend Running"}


@app.get("/articles")
async def fetch_articles(limit: int = 20):
    try:
        articles = get_latest_articles(limit=limit)
        return {"count": len(articles), "articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
def on_startup():
    # Start scheduler in background thread
    threading.Thread(target=start_scheduler, daemon=True).start()
