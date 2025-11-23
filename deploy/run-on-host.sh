#!/bin/bash

# 호스트 컴퓨터에서 실행하는 배포 스크립트
# ⚠️ 이 스크립트는 호스트 컴퓨터에서 실행해야 합니다!

set -e

# 현재 위치 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📂 프로젝트 디렉토리: $PROJECT_DIR"
cd "$PROJECT_DIR"

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

# Docker 컨테이너 시작
echo ""
echo "🐳 Docker 컨테이너 시작 중..."
cd "$PROJECT_DIR"

docker compose -f docker-compose.test.yml up -d --build

# 상태 확인
echo ""
echo "⏳ 컨테이너가 시작될 때까지 대기 중..."
sleep 5

echo ""
echo "✅ 배포 완료!"
echo ""
echo "📋 접속 정보:"
echo "   - 프론트엔드: http://localhost:8080"
echo "   - 백엔드 API: http://localhost:8080/api"
echo "   - 데이터베이스: localhost:5433"
echo ""
echo "📊 컨테이너 상태:"
docker compose -f docker-compose.test.yml ps
echo ""
echo "📝 로그 확인:"
echo "   docker compose -f docker-compose.test.yml logs -f"
echo ""
echo "🛑 중지:"
echo "   docker compose -f docker-compose.test.yml down"
echo ""
echo "🔄 재시작 (빠른 재시작):"
echo "   ./deploy/restart.sh"
echo ""
echo "📝 참고:"
echo "   - 코드 변경 없이 재시작: ./deploy/restart.sh"
echo "   - 코드 변경 후 재배포: ./deploy/run-on-host.sh"

