"""
간단한 CRUD API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict
from app.core.database import get_db
from app.core.crud import CRUDBase
from app.models.lotto import LottoNumber

router = APIRouter()

# CRUD 인스턴스 생성
lotto_crud = CRUDBase(LottoNumber)

@router.post("/create")
async def create_record(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """레코드 생성"""
    try:
        record = lotto_crud.create(db, **data)
        return {
            "success": True,
            "message": "레코드가 생성되었습니다",
            "data": {
                "id": record.id,
                "created_at": record.generated_at.isoformat() if hasattr(record, 'generated_at') else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get/{record_id}")
async def get_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """레코드 조회"""
    try:
        record = lotto_crud.get(db, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="레코드를 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": {
                "id": record.id,
                "numbers": record.numbers if hasattr(record, 'numbers') else None,
                "created_at": record.generated_at.isoformat() if hasattr(record, 'generated_at') else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """레코드 목록 조회"""
    try:
        records = lotto_crud.get_all(db, skip=skip, limit=limit)
        return {
            "success": True,
            "data": [
                {
                    "id": record.id,
                    "numbers": record.numbers if hasattr(record, 'numbers') else None,
                    "created_at": record.generated_at.isoformat() if hasattr(record, 'generated_at') else None
                }
                for record in records
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{record_id}")
async def update_record(
    record_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """레코드 업데이트"""
    try:
        record = lotto_crud.update(db, record_id, **data)
        if not record:
            raise HTTPException(status_code=404, detail="레코드를 찾을 수 없습니다")
        
        return {
            "success": True,
            "message": "레코드가 업데이트되었습니다",
            "data": {
                "id": record.id,
                "updated_at": record.generated_at.isoformat() if hasattr(record, 'generated_at') else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{record_id}")
async def delete_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """레코드 삭제"""
    try:
        success = lotto_crud.delete(db, record_id)
        if not success:
            raise HTTPException(status_code=404, detail="레코드를 찾을 수 없습니다")
        
        return {
            "success": True,
            "message": "레코드가 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
