"""X API v2 (recent search) で CCS 関連ポストを取得し、DBに保存する。
無料枠は読み取り件数の上限が厳しいため、必要な分だけ実行すること。
"""
import datetime
import requests

from .config import X_BEARER_TOKEN, SEARCH_QUERY
from .models import SessionLocal, Post, init_db

SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"


def fetch_posts(max_results: int = 100, query: str = None):
    if not X_BEARER_TOKEN:
        raise RuntimeError("X_BEARER_TOKEN is not set in .env")

    headers = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}
    params = {
        "query": query or SEARCH_QUERY,
        "max_results": max(10, min(max_results, 100)),
        "tweet.fields": "created_at,author_id",
        "expansions": "author_id",
        "user.fields": "username",
    }

    resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    tweets = data.get("data", [])
    users = {u["id"]: u["username"] for u in data.get("includes", {}).get("users", [])}

    init_db()
    session = SessionLocal()
    saved = 0
    try:
        for tweet in tweets:
            tweet_id = tweet["id"]
            if session.get(Post, tweet_id):
                continue  # already fetched

            author_id = tweet.get("author_id")
            username = users.get(author_id, author_id)

            post = Post(
                id=tweet_id,
                text=tweet["text"],
                author=username,
                posted_at=datetime.datetime.fromisoformat(
                    tweet["created_at"].replace("Z", "+00:00")
                ),
                url=f"https://x.com/{username}/status/{tweet_id}",
                fetched_at=datetime.datetime.utcnow(),
            )
            session.add(post)
            saved += 1
        session.commit()
    finally:
        session.close()

    return saved, len(tweets)


if __name__ == "__main__":
    saved, total = fetch_posts()
    print(f"取得: {total}件 / 新規保存: {saved}件")
