#!/usr/bin/env python3
"""
데이터베이스 테이블 생성 스크립트
"""
import sys
sys.path.append('/app/backend')

from app.core.database import engine, Base
from app.models import User, LottoNumber

def create_all_tables():
    """모든 테이블 생성"""
    print("🔧 데이터베이스 테이블 생성 시작...")
    
    try:
        # 모든 모델의 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("✅ 테이블 생성 완료!")
        
        # 생성된 테이블 확인
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 생성된 테이블 목록 ({len(tables)}개):")
        for table in tables:
            print(f"   ✓ {table}")
            
            # 각 테이블의 컬럼 정보
            columns = inspector.get_columns(table)
            print(f"     컬럼: {len(columns)}개")
            for col in columns[:5]:  # 처음 5개만 표시
                print(f"       - {col['name']}: {col['type']}")
            if len(columns) > 5:
                print(f"       ... 외 {len(columns) - 5}개")
            print()
            
        return True
        
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 DD Investment 데이터베이스 초기화")
    print("=" * 60)
    print()
    
    success = create_all_tables()
    
    print()
    print("=" * 60)
    if success:
        print("🎉 데이터베이스 설정이 완료되었습니다!")
    else:
        print("❌ 데이터베이스 설정에 실패했습니다.")
        sys.exit(1)
