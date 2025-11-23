"""
애플리케이션 설정 파일
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import model_validator


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 애플리케이션 기본 설정
    app_name: str = "DD Investment API"
    debug: bool = False
    environment: str = "development"
    
    # 데이터베이스 설정
    database_url: Optional[str] = None
    database_host: Optional[str] = None  # Google Cloud SQL 인스턴스 IP
    database_port: int = 5432
    database_name: Optional[str] = None  # 데이터베이스 이름
    database_user: Optional[str] = None  # 사용자명
    database_password: Optional[str] = None  # 비밀번호
    
    # Google Cloud SQL 설정
    gcp_project_id: Optional[str] = None
    gcp_region: Optional[str] = None
    gcp_instance_name: Optional[str] = None
    
    # Redis 설정 (캐싱용)
    redis_url: Optional[str] = None
    
    # 이메일 설정
    email_sender: Optional[str] = None
    email_password: Optional[str] = None
    frontend_url: str = "http://localhost:3000"
    
    # API 키들
    alpha_vantage_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    
    # 보안 설정
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @model_validator(mode="after")
    def assemble_database_url(self):
        """DATABASE_URL이 비어 있으면 개별 항목으로 조립한다."""
        if not self.database_url:
            has_parts = all([
                self.database_host,
                self.database_name,
                self.database_user,
                self.database_password,
            ])
            if has_parts:
                self.database_url = (
                    f"postgresql+psycopg2://{self.database_user}:{self.database_password}"
                    f"@{self.database_host}:{self.database_port}/{self.database_name}"
                )
            else:
                raise ValueError(
                    "DATABASE_URL이 비어 있으며, DATABASE_HOST/PORT/NAME/USER/PASSWORD 중 일부가 누락되었습니다. "
                    "./backend/.env을 갱신하고 컨테이너를 재생성(docker compose up -d --force-recreate --no-deps backend) 하세요."
                )
        return self


# 전역 설정 인스턴스
settings = Settings()
