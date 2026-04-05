from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base
import os

# 로컬: 현재 디렉토리 / 배포(Render 등): /tmp 사용 (재시작시 초기화되지만 자동 재크롤링)
_db_path = os.getenv("DATABASE_PATH", "./competitions.db")
DATABASE_URL = f"sqlite:///{_db_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
