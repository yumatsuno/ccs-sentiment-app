"""DBに保存済みで未分析のポストに対し、Claude APIで5段階感情判定を行う。"""
import json
import re
import datetime

import anthropic

from .config import ANTHROPIC_API_KEY
from .models import SessionLocal, Post, init_db

MODEL = "claude-haiku-4-5-20251001"

LABELS = {
    1: "非常にネガティブ",
    2: "ネガティブ",
    3: "ニュートラル",
    4: "ポジティブ",
    5: "非常にポジティブ",
}

SYSTEM_PROMPT = (
    "あなたはCCS（二酸化炭素回収・地下貯留）に関する日本語のSNS投稿を分析するアナリストです。"
    "投稿内容がCCSに対してどの程度ポジティブ/ネガティブかを5段階で判定してください。"
    "1=非常にネガティブ, 2=ネガティブ, 3=ニュートラル, 4=ポジティブ, 5=非常にポジティブ。"
    '出力は {"score": <1-5の整数>} のJSONのみを返してください。説明は不要です。'
)


def analyze_pending():
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    init_db()
    session = SessionLocal()
    analyzed = 0
    errors = []
    try:
        posts = session.query(Post).filter(Post.sentiment_score.is_(None)).all()
        for post in posts:
            try:
                message = client.messages.create(
                    model=MODEL,
                    max_tokens=50,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": post.text}],
                )
                content = message.content[0].text.strip()
                try:
                    score = int(json.loads(content)["score"])
                except (json.JSONDecodeError, KeyError, TypeError):
                    match = re.search(r'"score"\s*:\s*(\d)', content)
                    if not match:
                        match = re.search(r"[1-5]", content)
                    if not match:
                        raise ValueError(f"応答からスコアを抽出できません: {content!r}")
                    score = int(match.group(0)[-1])
            except Exception as e:
                errors.append(f"{post.id}: {e}")
                continue

            score = max(1, min(5, score))
            post.sentiment_score = score
            post.sentiment_label = LABELS[score]
            analyzed += 1
        session.commit()
    finally:
        session.close()

    if errors:
        print(f"分析エラー ({len(errors)}件):")
        for err in errors[:5]:
            print(f"  - {err}")

    return analyzed, errors


if __name__ == "__main__":
    n, errs = analyze_pending()
    print(f"分析完了: {n}件 / エラー: {len(errs)}件")
    for e in errs:
        print(f"  - {e}")
