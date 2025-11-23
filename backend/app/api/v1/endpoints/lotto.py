from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.services.lotto_service import LottoService
from app.models.lotto import LottoNumber
from app.core.database import get_db

router = APIRouter()

def get_lotto_service(db: Session = Depends(get_db)) -> LottoService:
    """로또 서비스 의존성"""
    return LottoService(db)

@router.get("/generate")
async def generate_lotto_numbers(
    user_id: Optional[int] = None,
    lotto_service: LottoService = Depends(get_lotto_service)
):
    """로또 번호 1세트 생성 (하루 한번 제한)"""
    try:
        # 오늘 이미 생성된 번호가 있는지 확인
        today_lotto = lotto_service.get_today_lotto(user_id)
        if today_lotto:
            numbers = [int(x) for x in today_lotto.numbers.split(",")]
            return {
                "success": True,
                "numbers": numbers,
                "is_new": False,
                "generated_at": today_lotto.generated_at.isoformat(),
                "message": "오늘 이미 생성된 번호입니다"
            }
        
        # 새 번호 생성
        numbers = lotto_service.generate_lotto_numbers()
        analysis = lotto_service.analyze_numbers(numbers)
        
        # DB에 저장
        lotto_record = lotto_service.save_lotto_numbers(numbers, user_id)
        
        return {
            "success": True,
            "numbers": numbers,
            "analysis": analysis,
            "is_new": True,
            "lotto_id": lotto_record.id,
            "generated_at": lotto_record.generated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generate-multiple")
async def generate_multiple_sets(count: int = 5):
    """로또 번호 여러 세트 생성"""
    if count < 1 or count > 20:
        raise HTTPException(status_code=400, detail="세트 수는 1-20 사이여야 합니다")
    
    try:
        results = lotto_service.generate_multiple_sets(count)
        return {
            "success": True,
            "sets": results,
            "total_sets": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_numbers(
    numbers: List[int],
    lotto_service: LottoService = Depends(get_lotto_service)
):
    """로또 번호 분석"""
    if len(numbers) != 6:
        raise HTTPException(status_code=400, detail="로또 번호는 6개여야 합니다")
    
    if not all(1 <= num <= 45 for num in numbers):
        raise HTTPException(status_code=400, detail="로또 번호는 1-45 사이여야 합니다")
    
    if len(set(numbers)) != 6:
        raise HTTPException(status_code=400, detail="중복된 번호가 있습니다")
    
    try:
        analysis = lotto_service.analyze_numbers(numbers)
        return {
            "success": True,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today")
async def get_today_lotto(
    user_id: Optional[int] = None,
    lotto_service: LottoService = Depends(get_lotto_service)
):
    """오늘 생성된 로또 번호 조회"""
    try:
        today_lotto = lotto_service.get_today_lotto(user_id)
        if not today_lotto:
            return {
                "success": False,
                "message": "오늘 생성된 로또 번호가 없습니다"
            }
        
        numbers = [int(x) for x in today_lotto.numbers.split(",")]
        return {
            "success": True,
            "numbers": numbers,
            "generated_at": today_lotto.generated_at.isoformat(),
            "is_viewed": today_lotto.is_viewed,
            "viewed_at": today_lotto.viewed_at.isoformat() if today_lotto.viewed_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-viewed/{lotto_id}")
async def mark_lotto_as_viewed(
    lotto_id: int,
    user_id: Optional[int] = None,
    lotto_service: LottoService = Depends(get_lotto_service)
):
    """로또 번호를 확인했음으로 표시"""
    try:
        success = lotto_service.mark_as_viewed(lotto_id, user_id)
        if success:
            return {"success": True, "message": "확인 상태가 업데이트되었습니다"}
        else:
            return {"success": False, "message": "로또 번호를 찾을 수 없습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_lotto_history(
    user_id: int,
    limit: int = 10,
    lotto_service: LottoService = Depends(get_lotto_service)
):
    """사용자의 로또 번호 히스토리 조회"""
    try:
        history = lotto_service.get_user_lotto_history(user_id, limit)
        return {
            "success": True,
            "history": [
                {
                    "id": record.id,
                    "numbers": [int(x) for x in record.numbers.split(",")],
                    "generated_at": record.generated_at.isoformat(),
                    "is_viewed": record.is_viewed,
                    "viewed_at": record.viewed_at.isoformat() if record.viewed_at else None
                }
                for record in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
