"""
스키마들
"""
from .base import BaseSchema
from .lotto import (
    LottoNumberBase,
    LottoNumberCreate,
    LottoNumberResponse,
)
from .user import (
    GenderEnum,
    RoleEnum,
    SubscriptionTypeEnum,
    UserBase,
    UserCreate,
    UserUpdate,
    UserPasswordChange,
    UserSubscriptionUpdate,
    UserResponse,
    UserDetailResponse,
    UserLoginRequest,
    UserLoginResponse,
)

__all__ = [
    "BaseSchema",
    # Lotto
    "LottoNumberBase",
    "LottoNumberCreate",
    "LottoNumberResponse",
    # User
    "GenderEnum",
    "RoleEnum",
    "SubscriptionTypeEnum",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPasswordChange",
    "UserSubscriptionUpdate",
    "UserResponse",
    "UserDetailResponse",
    "UserLoginRequest",
    "UserLoginResponse",
]


