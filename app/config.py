import os
from dotenv import load_dotenv

load_dotenv()

X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ccs_posts.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

SEARCH_QUERY = '(CCS OR "二酸化炭素貯留" OR CO2貯留 OR "炭素回収貯留") -is:retweet lang:ja'
