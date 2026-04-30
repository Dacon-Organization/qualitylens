# Data Pipeline Skills — Index
### Navigation & Pipeline Overview

> **Pipeline Position**: Stage 1 — Entry
> **Input**: Raw UCI SECOM CSV + Kaggle Smart Manufacturing CSV
> **Output**: 전처리된 DataFrame (X_train, X_test, y_train, y_test)
> **Downstream**: modeling/ (Stage 2)
> **Recommended model**: `sonnet` — 규칙 기반 전처리, 매핑 작업

---

## Files

| 파일 | 설명 |
|------|------|
| [dataset-specs.md](dataset-specs.md) | 데이터셋 상세 스펙, 컬럼 매핑 |
| [sensor-profiling.md](sensor-profiling.md) | 센서 프로파일링, 결측률/분포 분석 |
| [preprocessing.md](preprocessing.md) | 결측치 처리, 스케일링 |
| [feature-engineering.md](feature-engineering.md) | 피처 선택, 파생 피처 |
| [class-balance.md](class-balance.md) | SMOTE, 클래스 불균형 전략 |
| [data-leakage.md](data-leakage.md) | Data Leakage 방지 Pipeline |
| [streaming-sim.md](streaming-sim.md) | 실시간 시뮬레이터 구현 |

---

## Processing Flow

```
Raw CSV (UCI SECOM + Kaggle Smart Manufacturing)
  │
  ├─ 1. dataset-specs        → 스펙 확인, 컬럼 매핑, 레이블 통일
  ├─ 2. sensor-profiling     → 결측률/분포/이상치 분석, 센서 그룹핑
  ├─ 3. preprocessing        → 결측치 처리, 스케일링, 저분산 제거
  ├─ 4. feature-engineering  → 분산 필터링, 상관 제거, 파생 피처 생성
  ├─ 5. class-balance        → SMOTE (train only), 불균형 전략 결정
  ├─ 6. data-leakage         → Stratified Split, Leakage 검증
  └─ 7. streaming-sim        → 실시간 시뮬레이터 (데모용)
  │
  ▼
X_train, X_test, y_train, y_test  →  modeling/ (Stage 2)
```

---

## 데이터셋 요약

| 항목 | UCI SECOM | Kaggle Smart Manufacturing |
|------|-----------|---------------------------|
| 샘플 수 | 1,567 | 가변 |
| 피처 수 | 591 센서 | ~10 (temperature 등) |
| 타겟 | Pass=-1, Fail=1 | 다양 |
| 불균형 비율 | 6.6% 불량 (104/1567) | 데이터셋별 상이 |
