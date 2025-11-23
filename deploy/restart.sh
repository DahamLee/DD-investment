#!/bin/bash

# Docker 컨테이너 재시작 스크립트
# ⚠️ 이 스크립트는 호스트 컴퓨터에서 실행해야 합니다!
# 이미 빌드된 상태에서 빠르게 재시작할 때 사용합니다.

set -e

# 현재 위치 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📂 프로젝트 디렉토리: $PROJECT_DIR"
cd "$PROJECT_DIR"

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되어 있지 않습니다."
    exit 1
fi

# 프론트엔드 빌드 확인
if [ ! -d "$PROJECT_DIR/frontend/dist" ]; then
    echo "⚠️  프론트엔드 빌드 파일이 없습니다."
    echo "   먼저 ./deploy/run-on-host.sh를 실행해주세요."
    exit 1
fi

echo "✅ 프론트엔드 빌드 파일 확인 완료"

# Docker 컨테이너 시작
echo ""
echo "🐳 Docker 컨테이너 시작 중..."
docker compose -f docker-compose.test.yml up -d

# 상태 확인
echo ""
echo "⏳ 컨테이너가 시작될 때까지 대기 중..."
sleep 3

echo ""
echo "✅ 재시작 완료!"
echo ""
echo "📋 접속 정보:"
echo "   - 프론트엔드: http://localhost:8080"
echo "   - 백엔드 API: http://localhost:8080/api"
echo "   - 데이터베이스: localhost:5433"
echo ""
echo "📊 컨테이너 상태:"
docker compose -f docker-compose.test.yml ps

