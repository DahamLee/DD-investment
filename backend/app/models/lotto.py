from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class LottoNumber(BaseModel):
    """로또 번호 저장 모델"""
    __tablename__ = "lotto_numbers"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 로그인 사용자 ID (선택적)
    numbers = Column(String(50), nullable=False)  # "1,2,3,4,5,6" 형태로 저장
    generated_at = Column(DateTime, default=datetime.utcnow)
    date_key = Column(String(10), nullable=False)  # "2024-01-15" 형태로 저장 (하루 한번 제한용)
    is_viewed = Column(Boolean, default=False)  # 사용자가 확인했는지 여부
    viewed_at = Column(DateTime, nullable=True)  # 확인한 시간
    
    # 관계 설정
    user = relationship("User", back_populates="lotto_numbers")







