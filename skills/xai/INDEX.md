# xai/ — Stage 3: Explain

> **Pipeline Position**: Stage 3 — Explain
> **Input**: XGBoost 모델 + 예측 결과 + Threshold 테이블 from `modeling/`
> **Output**: SHAP 분석 결과 + 조치 가이드 메시지 + 알림 객체
> **Downstream**: `ui/` (Stage 4)
> **Recommended model**: `opus` — SHAP 해석, 조치 로직 설계는 고정밀 추론 필요

## 파일 목록

| 파일 | 역할 | 핵심 개념 |
|------|------|-----------|
| `shap-analysis.md` | SHAP 계산 및 시각화 규칙 | TreeExplainer, 글로벌/로컬 분석, 캐싱 전략 |
| `action-guide.md` | 조치 가이드 생성 로직 | SHAP + Threshold → 메시지, 시나리오 카탈로그 |
| `alert-rules.md` | 알림 레벨 및 패널 규칙 | 3단계 레벨, 색상 코딩, 알림 패널 |

## 처리 흐름

```
modeling/ output
  (XGBoost model .joblib + threshold_table + 예측 결과 CSV)
       │
       ▼
[shap-analysis.md]
  └─ TreeExplainer 초기화
  └─ shap_values 전체 테스트셋 사전 계산 + joblib 캐싱
  └─ 글로벌: Summary Plot, Feature Importance
  └─ 로컬: Waterfall plot, Force plot (배치별)
  └─ Dependence Plot: top-3 피처
       │
       ▼
[action-guide.md]
  └─ 실패 예측 배치 → |SHAP| 상위 N개 피처 추출
  └─ threshold_table 조회 → 현재값 vs 정상범위 비교
  └─ 조치 메시지 생성 (시나리오 A/B/C)
  └─ 원클릭 수락 → session_state 기록
       │
       ▼
[alert-rules.md]
  └─ fail_probability 구간별 레벨 분류 (Info/Warning/Danger)
  └─ 알림 패널: 최근 20건 (시간 역순)
  └─ 색상/아이콘 코딩
       │
       ▼
  ui/ (Stage 4) — 대시보드 표시
```

## 핵심 제약

- **실시간 요건**: 단일 배치 SHAP 계산 < 50ms (TreeExplainer는 O(TLD), 캐싱 전략 병행)
- **설명 가능성**: 상위 5개 피처로 fail 원인의 80%+ 설명 (공장 현장 이해 수준)
- **조치 메시지**: 한국어, 비전문가가 바로 읽고 조치 가능한 수준
- **MVP 전략**: P4 데모용 3개 시나리오 하드코딩, SHAP 사전 계산 캐싱
