from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from .models import SessionLocal, Post, init_db
from .fetch_x import fetch_posts
from .analyze import analyze_pending

app = FastAPI(title="CCS ポスト感情分析")

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, label: str = Query(default="")):
    session = SessionLocal()
    try:
        query = session.query(Post).order_by(Post.posted_at.desc())
        if label:
            query = query.filter(Post.sentiment_label == label)
        posts = query.all()
    finally:
        session.close()

    labels = ["非常にネガティブ", "ネガティブ", "ニュートラル", "ポジティブ", "非常にポジティブ"]
    return templates.TemplateResponse(
        request,
        "index.html",
        {"posts": posts, "labels": labels, "selected_label": label},
    )


@app.post("/fetch")
def trigger_fetch(max_results: int = 100):
    saved, total = fetch_posts(max_results=max_results)
    return {"fetched": total, "saved": saved}


@app.post("/analyze")
def trigger_analyze():
    n = analyze_pending()
    return {"analyzed": n}
