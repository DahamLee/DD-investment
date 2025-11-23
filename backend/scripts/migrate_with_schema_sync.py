"""
스키마 동기화 + 데이터 마이그레이션 통합 스크립트
개발계 → 운영계 마이그레이션 시 사용
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.sync_schema import compare_and_sync_schema
from scripts.migrate_database import migrate_database
import argparse
from typing import Optional
from datetime import datetime


def migrate_with_schema_sync(
    source_host: str,
    source_port: int,
    source_database: str,
    source_user: str,
    source_password: str,
    target_host: str,
    target_port: int,
    target_database: str,
    target_user: str,
    target_password: str,
    alembic_cfg_path: Optional[str] = None,
    schema: str = None,
    tables: list = None,
    skip_tables: list = None,
    skip_schema_sync: bool = False,
    dry_run: bool = False
):
    """
    스키마 동기화 후 데이터 마이그레이션 실행
    """
    print("=" * 60)
    print("🚀 통합 마이그레이션 시작 (스키마 동기화 + 데이터 복사)")
    print("=" * 60)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1단계: 스키마 동기화
    if not skip_schema_sync:
        print("📋 1단계: 스키마 동기화")
        print("-" * 60)
        schema_success, schema_info = compare_and_sync_schema(
            source_host=source_host,
            source_port=source_port,
            source_database=source_database,
            source_user=source_user,
            source_password=source_password,
            target_host=target_host,
            target_port=target_port,
            target_database=target_database,
            target_user=target_user,
            target_password=target_password,
            alembic_cfg_path=alembic_cfg_path,
            dry_run=dry_run
        )
        
        if not schema_success:
            print("❌ 스키마 동기화 실패. 데이터 마이그레이션을 중단합니다.")
            return False
        
        print()
        
        if dry_run:
            print("🔍 [DRY RUN] 스키마 동기화는 건너뛰고 데이터 마이그레이션만 확인합니다.")
            print()
    else:
        print("⏭️  스키마 동기화 건너뛰기 (--skip-schema-sync 옵션)")
        print()
    
    # 2단계: 데이터 마이그레이션
    print("📋 2단계: 데이터 마이그레이션")
    print("-" * 60)
    data_success = migrate_database(
        source_host=source_host,
        source_port=source_port,
        source_database=source_database,
        source_user=source_user,
        source_password=source_password,
        target_host=target_host,
        target_port=target_port,
        target_database=target_database,
        target_user=target_user,
        target_password=target_password,
        tables=tables,
        schema=schema,
        skip_tables=skip_tables
    )
    
    if not data_success:
        print("❌ 데이터 마이그레이션 실패.")
        return False
    
    print()
    print("=" * 60)
    print("✅ 통합 마이그레이션 완료!")
    print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='스키마 동기화 + 데이터 마이그레이션 통합 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 개발계 → 운영계 마이그레이션
  python scripts/migrate_with_schema_sync.py \\
    --source-host 121.134.7.122 \\
    --source-database finance_db \\
    --source-user postgres \\
    --source-password dev_password \\
    --target-host 34.64.149.167 \\
    --target-database finance_db \\
    --target-user postgres \\
    --target-password prod_password
        """
    )
    
    # 소스 DB 설정
    parser.add_argument('--source-host', required=True, help='소스 DB 호스트')
    parser.add_argument('--source-port', type=int, default=5432, help='소스 DB 포트')
    parser.add_argument('--source-database', required=True, help='소스 DB 이름')
    parser.add_argument('--source-user', required=True, help='소스 DB 사용자')
    parser.add_argument('--source-password', required=True, help='소스 DB 비밀번호')
    
    # 타겟 DB 설정
    parser.add_argument('--target-host', required=True, help='타겟 DB 호스트')
    parser.add_argument('--target-port', type=int, default=5432, help='타겟 DB 포트')
    parser.add_argument('--target-database', required=True, help='타겟 DB 이름')
    parser.add_argument('--target-user', required=True, help='타겟 DB 사용자')
    parser.add_argument('--target-password', required=True, help='타겟 DB 비밀번호')
    
    # 옵션
    parser.add_argument('--alembic-config', default=None, help='Alembic 설정 파일 경로 (기본: backend/alembic.ini)')
    parser.add_argument('--schema', help='스키마 이름 (예: finance)')
    parser.add_argument('--tables', nargs='+', help='복사할 테이블 목록')
    parser.add_argument('--skip-tables', nargs='+', help='건너뛸 테이블 목록')
    parser.add_argument('--skip-schema-sync', action='store_true', help='스키마 동기화 건너뛰기')
    parser.add_argument('--dry-run', action='store_true', help='실제로 변경하지 않고 확인만')
    
    args = parser.parse_args()
    
    success = migrate_with_schema_sync(
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
        alembic_cfg_path=args.alembic_config,
        schema=args.schema,
        tables=args.tables,
        skip_tables=args.skip_tables,
        skip_schema_sync=args.skip_schema_sync,
        dry_run=args.dry_run
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

