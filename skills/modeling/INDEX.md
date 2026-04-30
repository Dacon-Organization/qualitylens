# modeling/ — Stage 2: Predict

> **Pipeline Position**: Stage 2 — Predict
> **Input**: 전처리된 DataFrame from `data-pipeline/` (591 sensors, binary label)
> **Output**: 학습된 XGBoost 모델 (.joblib) + Threshold 테이블 + 예측 결과 CSV
> **Downstream**: `xai/` (Stage 3 — SHAP 해석), `ui/` (Stage 4 — 대시보드 표시)
> **Recommended model**: `opus` — 수학적 공식, 하이퍼파라미터 튜닝, 교차 검증 설계

## 파일 목록

| 파일 | 역할 | 핵심 개념 |
|------|------|-----------|
| `train-pipeline.md` | XGBoost 학습 파이프라인 | Stratified K-Fold, early stopping, scale_pos_weight |
| `evaluation.md` | 성능 평가 지표 및 시각화 | MCC (primary), PR-AUC, Youden's J threshold |
| `threshold-engine.md` | 센서 정상범위 계산 | PASS 제품 mean±2σ, 이상 감지 로직 |
| `model-ops.md` | 모델 저장/로드/관리 | joblib, SHAP 캐싱, model card |

## 처리 흐름

```
data-pipeline/ output
       │
       ▼
[train-pipeline.md]
  └─ scale_pos_weight 계산
  └─ Stratified K-Fold (k=5)
  └─ XGBoost fit + early stopping
  └─ per-fold MCC 기록
       │
       ├──────────────────────────┐
       ▼                          ▼
[evaluation.md]          [threshold-engine.md]
  MCC / PR-AUC             PASS 데이터 mean±2σ
  Youden's J               threshold_table 생성
  confusion matrix              │
       │                        │
       └────────────┬───────────┘
                    ▼
             [model-ops.md]
          joblib 저장, model card
          SHAP Explainer 캐싱
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       xai/             ui/ (Stage 4)
    (Stage 3)
```

## 핵심 제약

- **평가 지표**: MCC 최우선 (클래스 불균형 6.6% fail rate에 최적)
- **모델**: XGBoost binary:logistic
- **추론 속도**: 단일 샘플 < 10ms (실시간 라인 모니터링 요건)
- **재현성**: `random_state=42` 고정
