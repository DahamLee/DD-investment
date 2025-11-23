#!/bin/bash

# 프로덕션 배포 스크립트
# ⚠️ 이 스크립트는 호스트 컴퓨터에서 실행해야 합니다!
# ⚠️ 프로덕션 배포 전에 반드시 .env.production 파일을 확인하세요!

set -e

# 현재 위치 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📂 프로젝트 디렉토리: $PROJECT_DIR"
cd "$PROJECT_DIR"

# 개발 환경 변수 파일 확인 (임시로 .env.development 사용)
if [ ! -f "backend/.env.development" ]; then
    echo "❌ 개발 환경 변수 파일이 없습니다!"
    echo "   backend/.env.development 파일을 생성해주세요."
    exit 1
fi

# .env.development 파일에서 환경 변수 로드
# docker-compose.prod.yml에서 호스트 환경 변수를 참조하기 때문
if [ -f "backend/.env.development" ]; then
    # .env.development 파일의 모든 변수를 환경 변수로 export
    set -a  # 자동으로 export
    source backend/.env.development
    set +a  # 자동 export 해제
    
    if [ -z "$DATABASE_PASSWORD" ]; then
        echo "⚠️  DATABASE_PASSWORD가 .env.development에 없습니다."
        echo "   docker-compose.prod.yml에서 DATABASE_PASSWORD가 필요합니다."
    fi
fi

echo "⚠️  프로덕션 배포를 시작합니다 (개발 환경 변수 사용)..."
echo "   환경 변수 파일: backend/.env.development"

# 환경 변수로 확인 건너뛰기 가능 (CI/CD 등에서 사용)
if [ "${SKIP_CONFIRMATION:-}" != "true" ]; then
    # 터미널이 대화형인지 확인
    if [ -t 0 ]; then
        read -p "   계속하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ 배포가 취소되었습니다."
            exit 1
        fi
    else
        echo "⚠️  비대화형 환경입니다. 확인을 건너뜁니다."
        echo "   확인을 건너뛰려면: SKIP_CONFIRMATION=true ./deploy/run-prod.sh"
        sleep 2
    fi
fi

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    echo "   Docker를 먼저 설치해주세요: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose가 설치되어 있지 않습니다."
    echo "   Docker Compose를 설치해주세요."
    exit 1
fi

echo "✅ Docker 확인 완료"

# 프론트엔드 빌드 (Docker 사용)
echo ""
echo "📦 프론트엔드 빌드 중 (Docker 사용)..."
cd "$PROJECT_DIR"

# 임시 컨테이너로 빌드 수행
echo "🔨 Docker를 사용하여 프론트엔드 빌드 중..."
if ! docker run --rm \
    -v "$PROJECT_DIR/frontend:/app" \
    -w /app \
    node:20-alpine \
    sh -c "npm ci && npm run build"; then
    echo "❌ 프론트엔드 빌드 실패"
    exit 1
fi

# 빌드 결과 확인
if [ ! -d "$PROJECT_DIR/frontend/dist" ]; then
    echo "❌ 프론트엔드 빌드 실패: dist 폴더가 생성되지 않았습니다."
    exit 1
fi

echo "✅ 프론트엔드 빌드 완료"

# SSL 인증서 확인 (선택사항)
if [ -d "/etc/letsencrypt" ]; then
    echo "✅ SSL 인증서 확인됨"
else
    echo "⚠️  SSL 인증서가 없습니다. HTTPS가 작동하지 않을 수 있습니다."
    echo "   Let's Encrypt 인증서를 설치하려면:"
    echo "   sudo certbot --nginx -d yourdomain.com"
fi

# Docker 컨테이너 시작
echo ""
echo "🐳 Docker 컨테이너 시작 중 (프로덕션 모드)..."
cd "$PROJECT_DIR"

docker compose -f docker-compose.prod.yml up -d --build

# 상태 확인
echo ""
echo "⏳ 컨테이너가 시작될 때까지 대기 중..."
sleep 5

echo ""
echo "✅ 프로덕션 배포 완료!"
echo ""
echo "📋 접속 정보:"
echo "   - 프론트엔드: http://yourdomain.com (또는 https://yourdomain.com)"
echo "   - 백엔드 API: http://yourdomain.com/api (또는 https://yourdomain.com/api)"
echo "   - 데이터베이스: localhost:5432"
echo ""
echo "📊 컨테이너 상태:"
docker compose -f docker-compose.prod.yml ps
echo ""
echo "📝 로그 확인:"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 중지:"
echo "   docker compose -f docker-compose.prod.yml down"
echo ""
echo "🔄 재시작:"
echo "   docker compose -f docker-compose.prod.yml restart"
echo ""
echo "⚠️  중요 사항:"
echo "   - 프로덕션 환경에서는 반드시 HTTPS를 사용하세요"
echo "   - 환경 변수 파일(backend/.env.development)을 정기적으로 백업하세요"
echo "   - 데이터베이스 백업을 정기적으로 수행하세요"

