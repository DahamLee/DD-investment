"""
데이터베이스 마이그레이션 스크립트
다른 DB 서버에서 데이터를 현재 DB로 옮기는 도구
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings
import argparse
from typing import Optional
from datetime import datetime


def get_engine_from_config(host: str, port: int, database: str, user: str, password: str):
    """설정으로부터 SQLAlchemy 엔진 생성"""
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, echo=False)


def get_table_list(engine, schema: Optional[str] = None):
    """데이터베이스의 테이블 목록 가져오기"""
    inspector = inspect(engine)
    if schema:
        return inspector.get_table_names(schema=schema)
    else:
        tables = []
        schemas = inspector.get_schema_names()
        for sch in schemas:
            if sch not in ['information_schema', 'pg_catalog', 'pg_toast']:
                tables.extend([f"{sch}.{t}" for t in inspector.get_table_names(schema=sch)])
        return tables


def copy_table_data(source_engine, target_engine, table_name: str, schema: Optional[str] = None):
    """단일 테이블의 데이터를 복사"""
    full_table_name = f"{schema}.{table_name}" if schema else table_name
    
    print(f"  📋 테이블 복사 중: {full_table_name}")
    
    # 소스에서 데이터 읽기
    with source_engine.connect() as source_conn:
        result = source_conn.execute(text(f"SELECT * FROM {full_table_name}"))
        rows = result.fetchall()
        columns = result.keys()
        
        if not rows:
            print(f"    ⚠️  데이터가 없습니다. 건너뜁니다.")
            return 0
        
        print(f"    📊 {len(rows)}개 행 발견")
    
    # 타겟에 데이터 쓰기
    with target_engine.begin() as target_conn:
        # 기존 데이터 삭제 (선택사항)
        target_conn.execute(text(f"TRUNCATE TABLE {full_table_name} CASCADE"))
        
        # 데이터 삽입
        if rows:
            # 컬럼 목록 생성
            column_list = ", ".join(columns)
            placeholders = ", ".join([f":{col}" for col in columns])
            
            # 각 행을 딕셔너리로 변환
            for row in rows:
                row_dict = {col: val for col, val in zip(columns, row)}
                target_conn.execute(
                    text(f"INSERT INTO {full_table_name} ({column_list}) VALUES ({placeholders})"),
                    row_dict
                )
    
    print(f"    ✅ {len(rows)}개 행 복사 완료")
    return len(rows)


def migrate_database(
    source_host: str,
    source_port: int,
    source_database: str,
    source_user: str,
    source_password: str,
    target_host: Optional[str] = None,
    target_port: Optional[int] = None,
    target_database: Optional[str] = None,
    target_user: Optional[str] = None,
    target_password: Optional[str] = None,
    tables: Optional[list] = None,
    schema: Optional[str] = None,
    skip_tables: Optional[list] = None
):
    """
    데이터베이스 마이그레이션 실행
    
    Args:
        source_*: 소스 DB 연결 정보
        target_*: 타겟 DB 연결 정보 (None이면 현재 .env 설정 사용)
        tables: 복사할 테이블 목록 (None이면 모든 테이블)
        schema: 스키마 이름 (예: 'finance')
        skip_tables: 건너뛸 테이블 목록
    """
    print("=" * 60)
    print("🚀 데이터베이스 마이그레이션 시작")
    print("=" * 60)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 타겟 DB 설정 (없으면 현재 설정 사용)
    if target_host is None:
        settings = Settings()
        target_host = settings.database_host
        target_port = settings.database_port
        target_database = settings.database_name
        target_user = settings.database_user
        target_password = settings.database_password
        print("📌 타겟 DB: 현재 .env 설정 사용")
    else:
        print("📌 타겟 DB: 명령줄 인자 사용")
    
    print(f"📤 소스 DB: {source_user}@{source_host}:{source_port}/{source_database}")
    print(f"📥 타겟 DB: {target_user}@{target_host}:{target_port}/{target_database}")
    print()
    
    # 엔진 생성
    print("🔌 데이터베이스 연결 중...")
    source_engine = get_engine_from_config(
        source_host, source_port, source_database, source_user, source_password
    )
    target_engine = get_engine_from_config(
        target_host, target_port, target_database, target_user, target_password
    )
    
    # 연결 테스트
    try:
        with source_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 소스 DB 연결 성공")
    except Exception as e:
        print(f"❌ 소스 DB 연결 실패: {e}")
        return False
    
    try:
        with target_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 타겟 DB 연결 성공")
    except Exception as e:
        print(f"❌ 타겟 DB 연결 실패: {e}")
        return False
    
    print()
    
    # 테이블 목록 가져오기
    if schema:
        all_tables = get_table_list(source_engine, schema)
        all_tables = [t.replace(f"{schema}.", "") for t in all_tables if t.startswith(f"{schema}.")]
    else:
        all_tables = get_table_list(source_engine)
    
    # 복사할 테이블 결정
    if tables:
        tables_to_copy = [t for t in tables if t in all_tables]
    else:
        tables_to_copy = all_tables
    
    # 건너뛸 테이블 제외
    if skip_tables:
        tables_to_copy = [t for t in tables_to_copy if t not in skip_tables]
    
    # alembic_version은 자동으로 관리되므로 건너뛰기
    if 'alembic_version' in tables_to_copy:
        tables_to_copy.remove('alembic_version')
    
    print(f"📋 복사할 테이블: {len(tables_to_copy)}개")
    print(f"   {', '.join(tables_to_copy[:5])}{'...' if len(tables_to_copy) > 5 else ''}")
    print()
    
    # 외래키 제약조건 순서 고려 (간단한 순서: users -> finance.stock -> finance.financial_account -> finance.financial_statement_raw)
    ordered_tables = []
    priority_order = ['users', 'email_verifications', 'stock', 'financial_account', 'financial_statement_raw', 'lotto_numbers']
    
    for priority_table in priority_order:
        if priority_table in tables_to_copy:
            ordered_tables.append(priority_table)
            tables_to_copy.remove(priority_table)
    
    # 나머지 테이블 추가
    ordered_tables.extend(tables_to_copy)
    
    # 데이터 복사
    total_rows = 0
    for table in ordered_tables:
        try:
            rows = copy_table_data(source_engine, target_engine, table, schema)
            total_rows += rows
            print()
        except Exception as e:
            print(f"    ❌ 오류 발생: {e}")
            print()
    
    print("=" * 60)
    print(f"✅ 마이그레이션 완료!")
    print(f"📊 총 {total_rows}개 행 복사됨")
    print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return True


def main():
    parser = argparse.ArgumentParser(description='데이터베이스 마이그레이션 도구')
    
    # 소스 DB 설정
    parser.add_argument('--source-host', required=True, help='소스 DB 호스트')
    parser.add_argument('--source-port', type=int, default=5432, help='소스 DB 포트')
    parser.add_argument('--source-database', required=True, help='소스 DB 이름')
    parser.add_argument('--source-user', required=True, help='소스 DB 사용자')
    parser.add_argument('--source-password', required=True, help='소스 DB 비밀번호')
    
    # 타겟 DB 설정 (선택사항, 없으면 .env 사용)
    parser.add_argument('--target-host', help='타겟 DB 호스트 (없으면 .env 사용)')
    parser.add_argument('--target-port', type=int, help='타겟 DB 포트')
    parser.add_argument('--target-database', help='타겟 DB 이름')
    parser.add_argument('--target-user', help='타겟 DB 사용자')
    parser.add_argument('--target-password', help='타겟 DB 비밀번호')
    
    # 옵션
    parser.add_argument('--schema', help='스키마 이름 (예: finance)')
    parser.add_argument('--tables', nargs='+', help='복사할 테이블 목록 (공백으로 구분)')
    parser.add_argument('--skip-tables', nargs='+', help='건너뛸 테이블 목록')
    
    args = parser.parse_args()
    
    migrate_database(
        source_host=args.source_host,
        source_port=args.source_port,
        source_database=args.source_database,
        source_user=args.source_user,
        source_password=args.source_password,
        target_host=args.target_host,
        target_port=args.target_port,
        target_database=args.target_database,
        target_user=args.target_user,
        target_password=args.target_password,
        tables=args.tables,
        schema=args.schema,
        skip_tables=args.skip_tables
    )


if __name__ == "__main__":
    main()

