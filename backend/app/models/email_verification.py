"""
이메일 인증 모델
"""
from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from .base import BaseModel


class EmailVerification(BaseModel):
    """이메일 인증 코드 모델"""
    __tablename__ = "email_verifications"
    
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(String(10), default="false", nullable=False)  # "true" or "false"
    
    def __repr__(self):
        return f"<EmailVerification(email='{self.email}', code='{self.code}', expires_at='{self.expires_at}')>"
