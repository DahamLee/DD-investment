"""
간단한 CRUD 기능
"""
from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic, List, Optional, Any

ModelType = TypeVar("ModelType")

class CRUDBase(Generic[ModelType]):
    """기본 CRUD 클래스"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def create(self, db: Session, **kwargs) -> ModelType:
        """레코드 생성"""
        db_obj = self.model(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """ID로 레코드 조회"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """모든 레코드 조회"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: Any, **kwargs) -> Optional[ModelType]:
        """레코드 업데이트"""
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: Any) -> bool:
        """레코드 삭제"""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False
