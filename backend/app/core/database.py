"""
데이터베이스 연결 및 세션 관리
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

def get_database_url():
    """환경에 따라 데이터베이스 URL 생성"""
    if settings.database_host:
        # PostgreSQL 연결 (Google Cloud SQL)
        return f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"
    else:
        # SQLite 연결 (로컬 개발)
        return settings.database_url

# 데이터베이스 엔진 생성
engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 기본 모델 클래스
Base = declarative_base()


def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """데이터베이스 테이블 삭제"""
    Base.metadata.drop_all(bind=engine)
