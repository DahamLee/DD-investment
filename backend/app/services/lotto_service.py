import random
from typing import List, Dict, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.lotto import LottoNumber

class LottoService:
    """로또 번호 생성 서비스"""
    
    def __init__(self, db: Session = None):
        self.min_number = 1
        self.max_number = 45  # 한국 로또는 1-45
        self.number_count = 6
        self.db = db
    
    def generate_lotto_numbers(self) -> List[int]:
        """로또 번호 6개 생성 (중복 없음)"""
        numbers = random.sample(
            range(self.min_number, self.max_number + 1), 
            self.number_count
        )
        return sorted(numbers)
    
    def generate_multiple_sets(self, count: int = 5) -> List[Dict]:
        """여러 세트의 로또 번호 생성"""
        results = []
        for i in range(count):
            numbers = self.generate_lotto_numbers()
            results.append({
                "set_number": i + 1,
                "numbers": numbers,
                "generated_at": datetime.now().isoformat()
            })
        return results
    
    
    def analyze_numbers(self, numbers: List[int]) -> Dict:
        """로또 번호 분석 (홀짝, 구간별 분포 등)"""
        if len(numbers) != 6:
            raise ValueError("로또 번호는 6개여야 합니다")
        
        odd_count = sum(1 for num in numbers if num % 2 == 1)
        even_count = 6 - odd_count
        
        # 구간별 분포 (1-15, 16-30, 31-45)
        low_count = sum(1 for num in numbers if 1 <= num <= 15)
        mid_count = sum(1 for num in numbers if 16 <= num <= 30)
        high_count = sum(1 for num in numbers if 31 <= num <= 45)
        
        return {
            "numbers": numbers,
            "odd_count": odd_count,
            "even_count": even_count,
            "low_range": low_count,
            "mid_range": mid_count,
            "high_range": high_count,
            "sum": sum(numbers),
            "average": round(sum(numbers) / 6, 2)
        }
    
    def save_lotto_numbers(self, numbers: List[int], user_id: Optional[int] = None) -> LottoNumber:
        """로또 번호를 DB에 저장"""
        if not self.db:
            raise ValueError("Database session이 필요합니다")
        
        today = date.today().strftime("%Y-%m-%d")
        
        # 오늘 이미 생성된 번호가 있는지 확인
        existing = self.db.query(LottoNumber).filter(
            LottoNumber.date_key == today,
            LottoNumber.user_id == user_id
        ).first()
        
        if existing:
            return existing
        
        # 새 로또 번호 저장
        lotto_record = LottoNumber(
            user_id=user_id,
            numbers=",".join(map(str, numbers)),
            date_key=today,
            generated_at=datetime.utcnow()
        )
        
        self.db.add(lotto_record)
        self.db.commit()
        self.db.refresh(lotto_record)
        
        return lotto_record
    
    def get_today_lotto(self, user_id: Optional[int] = None) -> Optional[LottoNumber]:
        """오늘 생성된 로또 번호 조회"""
        if not self.db:
            return None
        
        today = date.today().strftime("%Y-%m-%d")
        return self.db.query(LottoNumber).filter(
            LottoNumber.date_key == today,
            LottoNumber.user_id == user_id
        ).first()
    
    def mark_as_viewed(self, lotto_id: int, user_id: Optional[int] = None) -> bool:
        """로또 번호를 확인했음으로 표시"""
        if not self.db:
            return False
        
        lotto = self.db.query(LottoNumber).filter(
            LottoNumber.id == lotto_id,
            LottoNumber.user_id == user_id
        ).first()
        
        if lotto:
            lotto.is_viewed = True
            lotto.viewed_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def get_user_lotto_history(self, user_id: int, limit: int = 10) -> List[LottoNumber]:
        """사용자의 로또 번호 히스토리 조회"""
        if not self.db:
            return []
        
        return self.db.query(LottoNumber).filter(
            LottoNumber.user_id == user_id
        ).order_by(LottoNumber.generated_at.desc()).limit(limit).all()
    