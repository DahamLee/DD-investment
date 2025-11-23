"""
사용자 모델
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel


class GenderEnum(str, enum.Enum):
    """성별"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class RoleEnum(str, enum.Enum):
    """사용자 역할"""
    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"


class SubscriptionTypeEnum(str, enum.Enum):
    """구독 타입"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(BaseModel):
    """사용자 모델 (완전형)"""
    __tablename__ = "users"
    
    # === 기본 식별 ===
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # === 인증 관련 ===
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    
    
    # === 개인정보 ===
    nickname = Column(String(50), unique=True, index=True, nullable=False)  # 닉네임 (화면 표시용, 필수)
    full_name = Column(String(100), nullable=True)  # 실명
    birth_date = Column(Date, nullable=True)  # 생년월일
    gender = Column(SQLEnum(GenderEnum), nullable=True)  # 성별
    phone = Column(String(20), nullable=True)  # 전화번호
    profile_image_url = Column(String(500), nullable=True)  # 프로필 이미지
    
    # === 마케팅/서비스 동의 ===
    marketing_agreed = Column(Boolean, default=False, nullable=False)
    marketing_agreed_at = Column(DateTime, nullable=True)
    terms_agreed = Column(Boolean, default=False, nullable=False)
    terms_agreed_at = Column(DateTime, nullable=True)
    privacy_agreed = Column(Boolean, default=False, nullable=False)
    privacy_agreed_at = Column(DateTime, nullable=True)
    
    # === 권한/역할 ===
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.USER, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    premium_expires_at = Column(DateTime, nullable=True)
    
    # === 구독 정보 ===
    subscription_type = Column(SQLEnum(SubscriptionTypeEnum), default=SubscriptionTypeEnum.FREE, nullable=False)
    subscription_started_at = Column(DateTime, nullable=True)  # 구독 시작일
    subscription_expires_at = Column(DateTime, nullable=True)  # 구독 만료일
    subscription_auto_renew = Column(Boolean, default=False, nullable=False)  # 자동 갱신 여부
    
    # === 보안/관리 ===
    login_count = Column(Integer, default=0, nullable=False)  # 로그인 횟수
    failed_login_attempts = Column(Integer, default=0, nullable=False)  # 로그인 실패 횟수
    locked_until = Column(DateTime, nullable=True)  # 계정 잠김 해제 시간
    deleted_at = Column(DateTime, nullable=True)  # 소프트 삭제 (탈퇴)
    
    # === 관계 설정 ===
    lotto_numbers = relationship("LottoNumber", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
