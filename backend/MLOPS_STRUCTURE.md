# MLOps 프로젝트 구조 가이드

## 📁 권장 프로젝트 구조

```
backend/
├── app/
│   ├── etl/                    # ETL 파이프라인
│   │   ├── __init__.py
│   │   ├── extract/            # 데이터 추출
│   │   │   ├── __init__.py
│   │   │   ├── stock_api.py     # 주식 API 데이터 추출
│   │   │   ├── financial_api.py # 재무제표 API 추출
│   │   │   └── news_api.py      # 뉴스 데이터 추출
│   │   ├── transform/           # 데이터 변환/전처리
│   │   │   ├── __init__.py
│   │   │   ├── clean.py         # 데이터 정제
│   │   │   ├── normalize.py     # 정규화
│   │   │   └── feature_engineering.py  # 특징 공학
│   │   ├── load/                # 데이터 로드
│   │   │   ├── __init__.py
│   │   │   ├── database.py      # DB 로드
│   │   │   └── cache.py          # 캐시 로드
│   │   ├── pipeline.py          # 전체 파이프라인 오케스트레이션
│   │   └── utils.py             # ETL 유틸리티
│   │
│   ├── ml/                      # ML 관련
│   │   ├── __init__.py
│   │   ├── training/            # 모델 학습
│   │   │   ├── __init__.py
│   │   │   ├── train.py         # 학습 스크립트
│   │   │   ├── models/          # 모델 정의
│   │   │   │   ├── __init__.py
│   │   │   │   ├── price_predictor.py  # 가격 예측 모델
│   │   │   │   └── sentiment_analyzer.py # 감성 분석 모델
│   │   │   └── config.py        # 학습 설정
│   │   ├── inference/           # 모델 추론
│   │   │   ├── __init__.py
│   │   │   ├── predictor.py     # 예측 서비스
│   │   │   └── preprocessor.py  # 추론 전처리
│   │   ├── evaluation/          # 모델 평가
│   │   │   ├── __init__.py
│   │   │   └── metrics.py       # 평가 지표
│   │   └── registry/            # 모델 레지스트리
│   │       ├── __init__.py
│   │       └── model_store.py   # 모델 저장/로드
│   │
│   ├── services/
│   │   └── ml_service.py        # ML 서빙 서비스
│   │
│   └── ... (기존 구조)
│
├── scripts/
│   ├── run_etl.py              # ETL 실행 스크립트
│   ├── train_model.py          # 모델 학습 스크립트
│   └── evaluate_model.py       # 모델 평가 스크립트
│
└── ml_artifacts/               # ML 아티팩트 저장
    ├── models/                 # 학습된 모델
    ├── data/                   # 처리된 데이터
    └── logs/                   # 학습 로그
```

## 🎯 현재 구조 vs 권장 구조

### 현재 구조
```
backend/app/etl/
├── fetch_api.py
├── preprocess.py
├── load.py
└── pipeline.py
```

### 권장 구조 (점진적 마이그레이션)
1. **단기**: 현재 구조 유지하되 기능 확장
2. **중기**: `extract/`, `transform/`, `load/` 서브디렉토리로 분리
3. **장기**: ML 디렉토리 추가 및 전체 구조 확장

## 📝 구조 선택 가이드

### 옵션 1: 현재 구조 유지 + 확장 (권장)
**장점:**
- 기존 코드와 호환
- 빠른 구현 가능
- 점진적 개선 가능

**구조:**
```
backend/app/etl/
├── fetch_api.py      # Extract
├── preprocess.py     # Transform
├── load.py           # Load
└── pipeline.py       # Orchestration
```

### 옵션 2: 완전 분리 구조
**장점:**
- 명확한 책임 분리
- 확장성 좋음
- 팀 협업에 유리

**구조:**
```
backend/app/etl/
├── extract/
├── transform/
└── load/
```

## 🚀 MLOps 워크플로우

```
1. 데이터 수집 (ETL)
   └── extract → transform → load

2. 모델 학습
   └── 데이터 준비 → 학습 → 평가 → 저장

3. 모델 서빙
   └── 모델 로드 → 전처리 → 추론 → 후처리

4. 모니터링
   └── 성능 모니터링 → 재학습 트리거
```

## 💡 추천 사항

**현재 단계에서는 옵션 1을 권장합니다:**
- 기존 구조 유지하면서 기능 확장
- ETL 파이프라인 완성 후 필요시 리팩토링
- ML 기능 추가 시 `ml/` 디렉토리 별도 생성


