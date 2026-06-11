from fastapi import FastAPI, Request, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from .config import SEARCH_QUERY
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
        {
            "posts": posts,
            "labels": labels,
            "selected_label": label,
            "search_query": SEARCH_QUERY,
        },
    )


@app.post("/fetch")
def trigger_fetch(search_query: str = Form(default=SEARCH_QUERY), max_results: int = Form(default=100)):
    fetch_posts(max_results=max_results, query=search_query)
    return RedirectResponse(url="/", status_code=303)


@app.post("/analyze")
def trigger_analyze():
    analyze_pending()
    return RedirectResponse(url="/", status_code=303)
