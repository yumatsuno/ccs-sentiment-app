from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import DATABASE_URL

Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True)  # X post ID
    text = Column(String, nullable=False)
    author = Column(String)
    posted_at = Column(DateTime)
    url = Column(String)
    sentiment_score = Column(Integer)  # 1-5
    sentiment_label = Column(String)
    fetched_at = Column(DateTime)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
