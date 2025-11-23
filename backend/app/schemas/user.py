"""
사용자 API 스키마
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime, date
from enum import Enum
import re


class GenderEnum(str, Enum):
    """성별"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class RoleEnum(str, Enum):
    """사용자 역할"""
    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"


class SubscriptionTypeEnum(str, Enum):
    """구독 타입"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# === 기본 스키마 ===
class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


# === 회원가입 ===
class UserCreate(UserBase):
    """사용자 생성 요청 (회원가입)"""
    password: str = Field(..., min_length=8, max_length=72, description="비밀번호는 최소 8자, 영문, 숫자, 특수문자를 포함해야 합니다")
    nickname: str = Field(..., min_length=2, max_length=50)  # 필수
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = None
    
    # 동의 필수
    terms_agreed: bool
    privacy_agreed: bool
    marketing_agreed: bool = False
    
    @validator('password')
    def validate_password_strength(cls, v):
        """비밀번호 강도 검증"""
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')
        
        # 영문 포함 (대소문자 구분 없음)
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('비밀번호는 영문을 포함해야 합니다')
        
        # 숫자 포함
        if not re.search(r'\d', v):
            raise ValueError('비밀번호는 숫자를 포함해야 합니다')
        
        # 특수문자 포함
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('비밀번호는 특수문자를 포함해야 합니다')
        
        return v


# === 프로필 수정 ===
class UserUpdate(BaseModel):
    """사용자 정보 수정"""
    nickname: Optional[str] = None
    phone: Optional[str] = None
    profile_image_url: Optional[str] = None
    marketing_agreed: Optional[bool] = None


# === 비밀번호 변경 ===
class UserPasswordChange(BaseModel):
    """비밀번호 변경"""
    old_password: str
    new_password: str = Field(..., min_length=8)


# === 구독 관리 ===
class UserSubscriptionUpdate(BaseModel):
    """구독 변경"""
    subscription_type: SubscriptionTypeEnum
    subscription_auto_renew: bool = False


# === 응답 스키마 ===
class UserResponse(UserBase):
    """사용자 기본 응답"""
    id: int
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    role: RoleEnum
    subscription_type: SubscriptionTypeEnum
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """사용자 상세 응답"""
    birth_date: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    
    # 구독 정보
    is_premium: bool
    premium_expires_at: Optional[datetime] = None
    subscription_started_at: Optional[datetime] = None
    subscription_expires_at: Optional[datetime] = None
    subscription_auto_renew: bool
    
    # 활동 정보
    last_login_at: Optional[datetime] = None
    login_count: int
    
    # 동의 정보
    marketing_agreed: bool
    terms_agreed: bool
    privacy_agreed: bool
    
    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    """로그인 요청"""
    username: str  # username 또는 email
    password: str


class UserLoginResponse(BaseModel):
    """로그인 응답"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

