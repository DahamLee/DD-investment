"""
로또 API 스키마
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LottoNumberBase(BaseModel):
    """로또 번호 기본 스키마"""
    numbers: str
    user_id: Optional[int] = None


class LottoNumberCreate(LottoNumberBase):
    """로또 번호 생성 요청"""
    date_key: str


class LottoNumberResponse(LottoNumberBase):
    """로또 번호 응답"""
    id: int
    generated_at: datetime
    date_key: str
    is_viewed: bool
    viewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


