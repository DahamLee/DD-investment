"""
기본 스키마 클래스
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BaseSchema(BaseModel):
    """모든 스키마의 기본 클래스"""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseResponse(BaseSchema):
    """기본 응답 스키마"""
    success: bool = True
    message: str = "Success"


