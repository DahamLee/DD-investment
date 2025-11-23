"""
스키마 동기화 스크립트
개발계와 운영계의 스키마를 동기화하는 도구
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
import argparse
from typing import Optional, Tuple
from datetime import datetime


def get_engine_from_config(host: str, port: int, database: str, user: str, password: str):
    """설정으로부터 SQLAlchemy 엔진 생성"""
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, echo=False)


def get_current_revision(engine) -> Optional[str]:
    """데이터베이스의 현재 Alembic 리비전 가져오기"""
    try:
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()
            return current_rev
    except Exception as e:
        # alembic_version 테이블이 없으면 None 반환
        if "does not exist" in str(e) or "alembic_version" in str(e).lower():
            return None
        raise


def get_head_revision(alembic_cfg: Config) -> str:
    """Alembic 스크립트의 최신(head) 리비전 가져오기"""
    script = ScriptDirectory.from_config(alembic_cfg)
    return script.get_current_head()


def upgrade_to_head(engine, alembic_cfg: Config, target_revision: Optional[str] = None):
    """데이터베이스를 최신 리비전으로 업그레이드"""
    # alembic_cfg의 sqlalchemy.url을 엔진의 URL로 설정
    url = str(engine.url)
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    
    if target_revision:
        command.upgrade(alembic_cfg, target_revision)
    else:
        command.upgrade(alembic_cfg, "head")


def compare_and_sync_schema(
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
    dry_run: bool = False
) -> Tuple[bool, dict]:
    """
    두 데이터베이스의 스키마를 비교하고 동기화
    
    Returns:
        (성공 여부, 정보 딕셔너리)
    """
    print("=" * 60)
    print("🔄 스키마 동기화 시작")
    print("=" * 60)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Alembic 설정 로드
    if alembic_cfg_path is None:
        # 기본 경로: backend/alembic.ini
        backend_dir = Path(__file__).parent.parent
        alembic_cfg_path = str(backend_dir / "alembic.ini")
    alembic_cfg = Config(alembic_cfg_path)
    
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
        return False, {}
    
    try:
        with target_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 타겟 DB 연결 성공")
    except Exception as e:
        print(f"❌ 타겟 DB 연결 실패: {e}")
        return False, {}
    
    print()
    
    # 현재 리비전 확인
    print("📊 마이그레이션 버전 확인 중...")
    source_revision = get_current_revision(source_engine)
    target_revision = get_current_revision(target_engine)
    head_revision = get_head_revision(alembic_cfg)
    
    print(f"📤 소스 DB 버전: {source_revision or '(마이그레이션 없음)'}")
    print(f"📥 타겟 DB 버전: {target_revision or '(마이그레이션 없음)'}")
    print(f"📦 최신 버전 (head): {head_revision}")
    print()
    
    info = {
        'source_revision': source_revision,
        'target_revision': target_revision,
        'head_revision': head_revision,
        'needs_sync': False,
        'sync_direction': None
    }
    
    # 동기화 필요 여부 확인
    if source_revision == target_revision:
        if source_revision == head_revision:
            print("✅ 두 DB 모두 최신 버전입니다. 동기화 불필요.")
            return True, info
        else:
            print(f"⚠️  두 DB는 동일하지만 최신 버전({head_revision})이 아닙니다.")
            info['needs_sync'] = True
            info['sync_direction'] = 'both_to_head'
    elif source_revision is None and target_revision is None:
        print("⚠️  두 DB 모두 마이그레이션이 없습니다. 최신 버전으로 업그레이드합니다.")
        info['needs_sync'] = True
        info['sync_direction'] = 'both_to_head'
    elif source_revision is None:
        print("⚠️  소스 DB에 마이그레이션이 없습니다. 타겟 DB 버전으로 동기화합니다.")
        info['needs_sync'] = True
        info['sync_direction'] = 'source_to_target'
    elif target_revision is None:
        print("⚠️  타겟 DB에 마이그레이션이 없습니다. 소스 DB 버전으로 동기화합니다.")
        info['needs_sync'] = True
        info['sync_direction'] = 'target_to_source'
    else:
        # 버전 비교 (간단한 비교, 실제로는 Alembic의 버전 체인을 따라가야 함)
        print(f"⚠️  버전이 다릅니다. 소스 DB를 기준으로 타겟 DB를 동기화합니다.")
        info['needs_sync'] = True
        info['sync_direction'] = 'target_to_source'
    
    if not info['needs_sync']:
        return True, info
    
    print()
    
    # 동기화 실행
    if dry_run:
        print("🔍 [DRY RUN] 실제로는 변경하지 않습니다.")
        print()
        if info['sync_direction'] == 'both_to_head':
            print(f"  → 소스 DB를 {head_revision}로 업그레이드")
            print(f"  → 타겟 DB를 {head_revision}로 업그레이드")
        elif info['sync_direction'] == 'target_to_source':
            print(f"  → 타겟 DB를 {source_revision}로 업그레이드")
        elif info['sync_direction'] == 'source_to_target':
            print(f"  → 소스 DB를 {target_revision}로 업그레이드")
        return True, info
    
    print("🚀 스키마 동기화 실행 중...")
    print()
    
    try:
        if info['sync_direction'] == 'both_to_head':
            print(f"📤 소스 DB를 {head_revision}로 업그레이드 중...")
            upgrade_to_head(source_engine, alembic_cfg)
            print("✅ 소스 DB 업그레이드 완료")
            print()
            
            print(f"📥 타겟 DB를 {head_revision}로 업그레이드 중...")
            upgrade_to_head(target_engine, alembic_cfg)
            print("✅ 타겟 DB 업그레이드 완료")
        elif info['sync_direction'] == 'target_to_source':
            print(f"📥 타겟 DB를 {source_revision}로 업그레이드 중...")
            upgrade_to_head(target_engine, alembic_cfg)
            # 소스가 최신이 아닐 수도 있으므로 head까지 업그레이드
            if source_revision != head_revision:
                print(f"📤 소스 DB를 {head_revision}로 업그레이드 중...")
                upgrade_to_head(source_engine, alembic_cfg)
            print("✅ 동기화 완료")
        elif info['sync_direction'] == 'source_to_target':
            print(f"📤 소스 DB를 {target_revision}로 업그레이드 중...")
            # 타겟이 최신이 아닐 수도 있으므로 head까지 업그레이드
            if target_revision != head_revision:
                print(f"📥 타겟 DB를 {head_revision}로 업그레이드 중...")
                upgrade_to_head(target_engine, alembic_cfg)
            print("✅ 동기화 완료")
        
        print()
        
        # 최종 버전 확인
        final_source_revision = get_current_revision(source_engine)
        final_target_revision = get_current_revision(target_engine)
        
        print("📊 최종 버전 확인:")
        print(f"  소스 DB: {final_source_revision}")
        print(f"  타겟 DB: {final_target_revision}")
        
        if final_source_revision == final_target_revision:
            print("✅ 스키마 동기화 성공!")
        else:
            print("⚠️  스키마가 여전히 다릅니다. 수동 확인이 필요합니다.")
            return False, info
        
    except Exception as e:
        print(f"❌ 동기화 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False, info
    
    print()
    print("=" * 60)
    print(f"✅ 스키마 동기화 완료!")
    print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return True, info


def main():
    parser = argparse.ArgumentParser(description='데이터베이스 스키마 동기화 도구')
    
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
    parser.add_argument('--alembic-config', default='alembic.ini', help='Alembic 설정 파일 경로')
    parser.add_argument('--dry-run', action='store_true', help='실제로 변경하지 않고 확인만')
    
    args = parser.parse_args()
    
    success, info = compare_and_sync_schema(
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
        dry_run=args.dry_run
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

