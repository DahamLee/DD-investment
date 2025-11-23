#!/bin/bash

# 테스트 배포 스크립트
# ⚠️ 호스트 컴퓨터 또는 컨테이너 내부에서 실행 가능

set -e

# 현재 위치 확인 (호스트 또는 컨테이너 모두 지원)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# /app 경로가 있으면 컨테이너 내부, 없으면 호스트
if [ -d "/app" ]; then
    WORK_DIR="/app"
else
    WORK_DIR="$PROJECT_DIR"
fi

echo "🚀 테스트 배포를 시작합니다..."
echo "📂 작업 디렉토리: $WORK_DIR"

# 1. 프론트엔드 빌드
echo "📦 프론트엔드 빌드 중..."
cd "$WORK_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "📥 npm 의존성 설치 중..."
    npm install
fi
echo "🔨 프로덕션 빌드 실행 중..."
npm run build
cd "$WORK_DIR"

# 2. Docker 이미지 빌드 및 컨테이너 실행
echo "🐳 Docker 컨테이너 시작 중..."
docker compose -f docker-compose.test.yml up -d --build

# 3. 상태 확인
echo "⏳ 컨테이너가 시작될 때까지 대기 중..."
sleep 5

echo "✅ 배포 완료!"
echo ""
echo "📋 접속 정보:"
echo "   - 프론트엔드: http://localhost:8080"
echo "   - 백엔드 API: http://localhost:8080/api"
echo "   - 데이터베이스: localhost:5433"
echo ""
echo "📊 컨테이너 상태 확인:"
docker compose -f docker-compose.test.yml ps
echo ""
echo "📝 로그 확인:"
echo "   docker compose -f docker-compose.test.yml logs -f"
echo ""
echo "🛑 중지:"
echo "   docker compose -f docker-compose.test.yml down"





